from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
from auth_service import get_current_user
import httpx
import os

logger = logging.getLogger(__name__)
rating_router = APIRouter(prefix="/api/ratings", tags=["ratings"])

class RatingRequest(BaseModel):
    anime_id: int
    rating: int  # 1 to 5

@rating_router.get("")
async def get_user_ratings(request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    ratings_cursor = db.ratings.find({"user_id": user["user_id"]}, {"_id": 0})
    ratings = await ratings_cursor.to_list(length=1000)
    return {"ratings": ratings}

@rating_router.post("")
async def submit_rating(payload: RatingRequest, request: Request, user = Depends(get_current_user)):
    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
    db = request.app.state.db
    await db.ratings.update_one(
        {"user_id": user["user_id"], "anime_id": payload.anime_id},
        {"$set": {
            "user_id": user["user_id"],
            "anime_id": payload.anime_id,
            "rating": payload.rating,
            "updated_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    return {"ok": True, "anime_id": payload.anime_id, "rating": payload.rating}

# We also want an endpoint to give recommendations
@rating_router.get("/recommendations")
async def get_recommendations(request: Request, user = Depends(get_current_user)):
    db = request.app.state.db
    ratings_cursor = db.ratings.find({"user_id": user["user_id"]}, {"_id": 0})
    ratings = await ratings_cursor.to_list(length=1000)
    
    # Simple recommendation:
    # 1. Fetch Prime catalog (we can just call the prime endpoint or use AniList directly, but we can't easily import the cache here without circular deps maybe)
    # Actually, we can fetch from our own /api/prime/catalog
    
    try:
        # Use our own endpoint locally
        backend_url = os.environ.get('BACKEND_INTERNAL_URL', 'http://127.0.0.1:8001') + '/api/prime/catalog?limit=240'
        async with httpx.AsyncClient() as client:
            r = await client.get(backend_url)
            r.raise_for_status()
            catalog = r.json().get("items", [])
    except Exception as e:
        logger.error(f"Failed to fetch catalog for recommendations: {e}")
        catalog = []
        
    if not ratings:
        # No ratings? Return top 10 from catalog
        return {"recommendations": catalog[:10]}
        
    # User has ratings
    # Find genres from animes they rated >= 4
    high_rated_ids = [r["anime_id"] for r in ratings if r["rating"] >= 4]
    low_rated_ids = [r["anime_id"] for r in ratings if r["rating"] <= 2]
    all_rated_ids = [r["anime_id"] for r in ratings]
    
    preferred_genres = {}
    for item in catalog:
        if item["id"] in high_rated_ids:
            for g in item.get("genres", []):
                preferred_genres[g] = preferred_genres.get(g, 0) + 1
                
    # If no preferred genres (rated everything < 4), just return unrated stuff
    unrated_catalog = [item for item in catalog if item["id"] not in all_rated_ids]
    
    if not preferred_genres:
        return {"recommendations": unrated_catalog[:10]}
        
    # Sort unrated catalog by how many preferred genres they have
    def score_item(item):
        s = 0
        for g in item.get("genres", []):
            s += preferred_genres.get(g, 0)
        return s
        
    unrated_catalog.sort(key=score_item, reverse=True)
    return {"recommendations": unrated_catalog[:10]}
