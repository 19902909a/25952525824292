from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging
from auth_service import get_current_user

logger = logging.getLogger(__name__)
profile_router = APIRouter(prefix="/api/profile", tags=["profile"])

# ==== Models ====
class Address(BaseModel):
    street: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = ""

class PremiumFeatures(BaseModel):
    banner_url: str = ""
    avatar_frame: str = "default"  # neon, fire, gold
    profile_aura: str = "#ffffff"
    title: str = "Otaku Novice"
    unlocked_titles: List[str] = ["Otaku Novice"]

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    picture: Optional[str] = None
    push_enabled: Optional[bool] = None
    address: Optional[Address] = None
    premium: Optional[PremiumFeatures] = None

# ==== Routes ====
@profile_router.get("/me")
async def get_my_profile(request: Request, user=Depends(get_current_user)):
    db = request.app.state.db
    user_id = user["user_id"]
    
    # Fetch full profile from a separate collection or the users collection.
    # Let's keep it in users collection.
    full_user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not full_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Ensure default fields exist
    defaults = {
        "bio": "Amoureux des animes et de la culture japonaise.",
        "phone": "",
        "address": {"street": "", "city": "", "postal_code": "", "country": ""},
        "wishlist": [], # List of anime IDs or product IDs
        "history": [],
        "push_enabled": False,
        "rewards": {
            "lova_coins": 150,
            "xp": 1250,
            "level": 5,
            "rank": "Silver",
            "watch_time_mins": 340
        },
        "premium": {
            "banner_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=2000",
            "avatar_frame": "default",
            "profile_aura": "#38bdf8",
            "title": "Otaku Novice",
            "unlocked_titles": ["Otaku Novice", "Explorateur", "Cinéphile"]
        }
    }
    
    needs_update = False
    for k, v in defaults.items():
        if k not in full_user:
            full_user[k] = v
            needs_update = True
            
    if needs_update:
        await db.users.update_one({"user_id": user_id}, {"$set": full_user})
        
    return full_user

@profile_router.get("/history")
async def get_history(request: Request, user=Depends(get_current_user)):
    db = request.app.state.db
    user_id = user["user_id"]
    full_user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not full_user:
        raise HTTPException(status_code=404, detail="User not found")
    history = full_user.get("history", [])
    return history

class HistoryItem(BaseModel):
    video_id: str
    title: str
    image: str
    progress: int = 0
    duration: int = 0

@profile_router.post("/history")
async def add_history(item: HistoryItem, request: Request, user=Depends(get_current_user)):
    db = request.app.state.db
    user_id = user["user_id"]
    
    full_user = await db.users.find_one({"user_id": user_id})
    history = full_user.get("history", [])
    
    # Remove if exists to move to top
    history = [h for h in history if h.get("video_id") != item.video_id]
    
    # Add to top
    new_item = item.model_dump()
    new_item["timestamp"] = datetime.utcnow().isoformat()
    history.insert(0, new_item)
    
    # Keep last 50
    history = history[:50]
        
    await db.users.update_one({"user_id": user_id}, {"$set": {"history": history}})
    return {"status": "success", "history": history}

@profile_router.put("/me")
async def update_my_profile(update_data: UserProfileUpdate, request: Request, user=Depends(get_current_user)):
    db = request.app.state.db
    user_id = user["user_id"]
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if not update_dict:
        return {"status": "no changes"}
        
    await db.users.update_one({"user_id": user_id}, {"$set": update_dict})
    
    updated_user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return updated_user

@profile_router.post("/wishlist")
async def toggle_wishlist(request: Request, item_id: str, user=Depends(get_current_user)):
    db = request.app.state.db
    user_id = user["user_id"]
    
    full_user = await db.users.find_one({"user_id": user_id})
    wishlist = full_user.get("wishlist", [])
    
    if item_id in wishlist:
        wishlist.remove(item_id)
        action = "removed"
    else:
        wishlist.append(item_id)
        action = "added"
        
    await db.users.update_one({"user_id": user_id}, {"$set": {"wishlist": wishlist}})
    return {"status": "success", "action": action, "wishlist": wishlist}

