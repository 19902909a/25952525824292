from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List
from auth_service import get_current_user

favorites_router = APIRouter(prefix="/api/favorites", tags=["favorites"])

class FavoriteAdd(BaseModel):
    anime_id: int

@favorites_router.get("")
async def get_favorites(request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    doc = await db.user_favorites.find_one({"user_id": user["user_id"]})
    if not doc:
        return {"favorites": []}
    return {"favorites": doc.get("anime_ids", [])}

@favorites_router.post("")
async def add_favorite(payload: FavoriteAdd, request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    await db.user_favorites.update_one(
        {"user_id": user["user_id"]},
        {"$addToSet": {"anime_ids": payload.anime_id}},
        upsert=True
    )
    return {"ok": True}

@favorites_router.delete("/{anime_id}")
async def remove_favorite(anime_id: int, request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    await db.user_favorites.update_one(
        {"user_id": user["user_id"]},
        {"$pull": {"anime_ids": anime_id}}
    )
    return {"ok": True}
