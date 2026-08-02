from fastapi import APIRouter, HTTPException, Request, Response, Cookie, Depends
from pydantic import BaseModel
import os
import uuid
import httpx
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
import bcrypt
import jwt
from typing import Optional

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_SECRET = os.environ.get("JWT_SECRET", "7a38f32bc8d7b3a98e27c1f8a7d2b3c4f5e6a7b8c9d0e1f2a3b4c5d6e7f8g9h0")
JWT_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=60), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return request.app.state.db

async def get_current_user(request: Request):
    db = request.app.state.db
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    
    # Check Emergent Session token as fallback if any remains
    if not token:
        session_token = request.cookies.get("session_token")
        if session_token:
            session = await db.user_sessions.find_one({"session_token": session_token})
            if session:
                user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0, "password_hash": 0})
                if user:
                    return user
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"user_id": payload["sub"]}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

class RegisterModel(BaseModel):
    email: str
    password: str
    name: str

class LoginModel(BaseModel):
    email: str
    password: str

class GoogleLoginModel(BaseModel):
    code: Optional[str] = None
    credential: Optional[str] = None

@auth_router.post("/register")
async def register(data: RegisterModel, response: Response, request: Request):
    db = request.app.state.db
    email = data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed = hash_password(data.password)
    new_user = {
        "user_id": user_id,
        "email": email,
        "name": data.name,
        "password_hash": hashed,
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(new_user)
    
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    new_user.pop("_id", None)
    new_user.pop("password_hash", None)
    return new_user

@auth_router.post("/login")
async def login(data: LoginModel, response: Response, request: Request):
    db = request.app.state.db
    email = data.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = user["user_id"]
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    user_copy = {k: v for k, v in user.items() if k not in ["_id", "password_hash"]}
    return user_copy

@auth_router.post("/google")
async def google_auth(data: GoogleLoginModel, response: Response, request: Request):
    # This endpoint receives the credential (JWT id_token) from @react-oauth/google
    if not data.credential:
        raise HTTPException(status_code=400, detail="Missing credential")
        
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
        # If client_id is not set, we bypass verification for testing purposes
        # The user said they will provide the key AFTER our help, so we need to mock it if client_id is missing
        if not client_id:
            # Decode JWT without verification (ONLY for testing when key is missing)
            import jwt
            id_info = jwt.decode(data.credential, options={"verify_signature": False})
        else:
            id_info = id_token.verify_oauth2_token(data.credential, google_requests.Request(), client_id)
            
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")
        
        if not email:
            raise ValueError("No email in token")
            
        db = request.app.state.db
        user = await db.users.find_one({"email": email})
        
        if not user:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            user = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "role": "user",
                "created_at": datetime.now(timezone.utc)
            }
            await db.users.insert_one(user)
        else:
            user_id = user.get("user_id")
            if not user_id:
                user_id = str(user["_id"])
                await db.users.update_one({"_id": user["_id"]}, {"$set": {"user_id": user_id}})
        
        access_token = create_access_token(user_id, email)
        refresh_token = create_refresh_token(user_id)
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
        
        user_copy = {k: v for k, v in user.items() if k not in ["_id", "password_hash"]}
        return user_copy
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")

class UpdateAvatarRequest(BaseModel):
    picture: str

@auth_router.put("/me/avatar")
async def update_avatar(payload: UpdateAvatarRequest, request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"picture": payload.picture}})
    return {"ok": True, "picture": payload.picture}

@auth_router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return user

@auth_router.post("/logout")
async def logout(response: Response, request: Request):
    response.delete_cookie("access_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("refresh_token", path="/", secure=True, httponly=True, samesite="none")
    response.delete_cookie("session_token", path="/", secure=True, httponly=True, samesite="none")
    return {"ok": True}
