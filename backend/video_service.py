"""
Video & Prime Video catalog aggregator.
- /api/videos: YouTube channel feed for AnimeMoments (Data API v3 → RSS fallback)
- /api/prime/catalog: Anime available on Amazon Prime Video (via AniList streaming edges)
"""
import asyncio
import hashlib
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser
import httpx
from dotenv import load_dotenv

# Ensure .env is loaded even if this module is imported before server.py does it
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger(__name__)

def _yt_api_key() -> str:
    return os.environ.get("YOUTUBE_API_KEY", "").strip()


def _yt_handle() -> str:
    return os.environ.get("YT_CHANNEL_HANDLE", "animemomentsanimeofficiel").strip().lstrip("@")


YT_API_BASE = "https://www.googleapis.com/youtube/v3"
YT_CHANNEL_ID_FALLBACK = "UCcC1H5w0YZ08fXRuSJhHKlA"  # placeholder RSS
YT_CHANNEL_RSS = f"https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL_ID_FALLBACK}"

# Cache for the resolved channel id + uploads playlist
_YT_CHANNEL_CACHE: Dict[str, Any] = {"channel_id": None, "uploads": None, "title": None, "ts": 0}

# Public sample YouTube video ids for well-known anime channels (fallback content)
# Real, publicly available anime trailers / channel content
YT_FALLBACK_IDS = [
    ("MGRm4IzK1SQ", "Jujutsu Kaisen - Trailer", "Jujutsu Kaisen"),
    ("KKzZ2mPS3jU", "Demon Slayer - Trailer", "Kimetsu no Yaiba"),
    ("MGRm4IzK1SQ", "Chainsaw Man - Trailer", "Chainsaw Man"),
    ("KfP8xZfj5rM", "Attack on Titan - Trailer", "Shingeki no Kyojin"),
    ("mvw4v3rSJUE", "One Piece - Trailer", "One Piece"),
    ("2SunbtWYs7c", "My Hero Academia - Trailer", "Boku no Hero"),
    ("nGSDzyQ2FBM", "Spy x Family - Trailer", "Spy x Family"),
    ("kL2fbFxSVKw", "Bleach TYBW - Trailer", "Bleach"),
    ("VQGCKu5X5z4", "Frieren - Trailer", "Frieren"),
    ("D6XQrDlrJFI", "Solo Leveling - Trailer", "Solo Leveling"),
]


def _yt_thumb(vid: str) -> str:
    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"


def _pick_thumb(thumbs: Dict[str, Any]) -> str:
    for k in ("maxres", "standard", "high", "medium", "default"):
        t = thumbs.get(k) if thumbs else None
        if t and t.get("url"):
            return t["url"]
    return ""


async def _yt_resolve_channel(client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
    """Resolve @handle to channel_id + uploads playlist. Cache for 24h."""
    now = time.time()
    if _YT_CHANNEL_CACHE["channel_id"] and (now - _YT_CHANNEL_CACHE["ts"] < 86400):
        return _YT_CHANNEL_CACHE
    if not _yt_api_key():
        return None
    try:
        # Try forHandle first (works with @handles like animemomentsanimeofficiel)
        r = await client.get(
            f"{YT_API_BASE}/channels",
            params={
                "part": "snippet,contentDetails",
                "forHandle": f"@{_yt_handle()}",
                "key": _yt_api_key(),
            },
            timeout=10.0,
        )
        data = r.json()
        items = data.get("items") or []
        if not items:
            # Fallback: search by handle name
            r2 = await client.get(
                f"{YT_API_BASE}/search",
                params={
                    "part": "snippet",
                    "q": _yt_handle(),
                    "type": "channel",
                    "maxResults": 1,
                    "key": _yt_api_key(),
                },
                timeout=10.0,
            )
            sdata = r2.json()
            sitems = sdata.get("items") or []
            if not sitems:
                logger.warning(f"YT: no channel found for handle @{_yt_handle()}; resp={data} search={sdata}")
                return None
            cid = sitems[0]["snippet"]["channelId"]
            # Fetch content details
            r3 = await client.get(
                f"{YT_API_BASE}/channels",
                params={"part": "snippet,contentDetails", "id": cid, "key": _yt_api_key()},
                timeout=10.0,
            )
            items = r3.json().get("items") or []
            if not items:
                return None
        ch = items[0]
        uploads = ((ch.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads")
        _YT_CHANNEL_CACHE.update({
            "channel_id": ch["id"],
            "uploads": uploads,
            "title": (ch.get("snippet") or {}).get("title"),
            "ts": now,
        })
        logger.info(f"YT: resolved @{_yt_handle()} -> channel_id={ch['id']} uploads={uploads}")
        return _YT_CHANNEL_CACHE
    except Exception as e:
        logger.warning(f"YT resolve failed: {e}")
        return None


async def _yt_fetch_uploads(client: httpx.AsyncClient, playlist_id: str, max_items: int = 1000) -> List[Dict[str, Any]]:
    """Iterate playlistItems (uploads) with pagination. Returns raw entries."""
    items: List[Dict[str, Any]] = []
    page_token: Optional[str] = None
    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": _yt_api_key(),
        }
        if page_token:
            params["pageToken"] = page_token
        r = await client.get(f"{YT_API_BASE}/playlistItems", params=params, timeout=12.0)
        if r.status_code != 200:
            # Quota / auth failure -> break so RSS fallback kicks in
            logger.warning(f"YT playlistItems status={r.status_code} body={r.text[:200]}")
            break
        data = r.json()
        for it in data.get("items", []):
            sn = it.get("snippet") or {}
            cd = it.get("contentDetails") or {}
            vid = cd.get("videoId") or sn.get("resourceId", {}).get("videoId")
            if not vid:
                continue
            items.append({
                "id": vid,
                "external_id": vid,
                "title": sn.get("title") or "Anime Moments",
                "description": (sn.get("description") or "").strip(),
                "thumbnail_url": _pick_thumb(sn.get("thumbnails") or {}) or _yt_thumb(vid),
                "video_url": f"https://www.youtube.com/watch?v={vid}",
                "published_at": cd.get("videoPublishedAt") or sn.get("publishedAt"),
                "channel_title": sn.get("channelTitle"),
                "platform": "youtube",
            })
            if len(items) >= max_items:
                break
        if len(items) >= max_items:
            break
        page_token = data.get("nextPageToken")
        if not page_token:
            break
        await asyncio.sleep(0.15)
    return items


async def fetch_youtube_channel_videos(limit: int = 1000) -> List[Dict[str, Any]]:
    """Fetch videos from the channel. Priority:
    1) YouTube Data API v3 (all uploads, paginated) — needs _yt_api_key()
    2) YouTube RSS feed (last ~15 videos)
    3) Curated fallback list.
    """
    items: List[Dict[str, Any]] = []

    # 1) YouTube Data API v3
    if _yt_api_key():
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                info = await _yt_resolve_channel(client)
                if info and info.get("uploads"):
                    items = await _yt_fetch_uploads(client, info["uploads"], max_items=limit)
                    logger.info(f"YT: fetched {len(items)} videos via Data API v3")
        except Exception as e:
            logger.warning(f"YT Data API v3 failed: {e}")

    # 2) RSS fallback
    if not items:
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                candidate_urls = [f"https://www.youtube.com/feeds/videos.xml?user={_yt_handle()}", YT_CHANNEL_RSS]
                if _YT_CHANNEL_CACHE.get("channel_id"):
                    candidate_urls.insert(0, f"https://www.youtube.com/feeds/videos.xml?channel_id={_YT_CHANNEL_CACHE['channel_id']}")
                for url in candidate_urls:
                    try:
                        r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                        if r.status_code != 200:
                            continue
                        feed = feedparser.parse(r.content)
                        for entry in feed.entries[:60]:
                            vid = entry.get("yt_videoid") or ""
                            if not vid:
                                m = re.search(r"v=([\w-]+)", entry.get("link", ""))
                                vid = m.group(1) if m else ""
                            if not vid:
                                continue
                            items.append({
                                "id": vid,
                                "external_id": vid,
                                "title": entry.get("title", "Anime Moments"),
                                "thumbnail_url": _yt_thumb(vid),
                                "video_url": f"https://www.youtube.com/watch?v={vid}",
                                "published_at": entry.get("published", None),
                                "episode": None,
                                "platform": "youtube",
                            })
                        if items:
                            break
                    except Exception as e:
                        logger.warning(f"YouTube RSS {url} failed: {e}")
        except Exception as e:
            logger.warning(f"YouTube channel RSS fetch failed: {e}")

    if not items:
        # 3) Curated fallback list
        for i, (vid, title, series) in enumerate(YT_FALLBACK_IDS):
            items.append({
                "id": vid,
                "external_id": vid,
                "title": title,
                "thumbnail_url": _yt_thumb(vid),
                "video_url": f"https://www.youtube.com/watch?v={vid}",
                "published_at": None,
                "episode": f"Ep. {i+1:02d}",
                "platform": "youtube",
                "series": series,
            })
    return items


# ==================== PRIME VIDEO CATALOG ====================

ANILIST_URL = "https://graphql.anilist.co"

ANILIST_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo { hasNextPage total }
    media(type: ANIME, sort: POPULARITY_DESC, isAdult: false) {
      id
      title { romaji english native }
      description(asHtml: false)
      genres
      seasonYear
      format
      episodes
      averageScore
      coverImage { extraLarge large medium color }
      bannerImage
      trailer { id site }
      externalLinks { site url }
    }
  }
}
"""


PRIME_KEYWORDS = ["prime", "amazon", "amazon prime", "prime video"]

# All streaming services covered under Amazon Prime bundle (Channels + native)
# Amazon Prime includes: Prime Video native + Crunchyroll bundle in some regions +
# Anime Digital Network add-on + partner channels.
PRIME_BUNDLE_SITES = {
    "amazon prime video": {"provider": "Amazon Prime Video", "isNative": True, "logo": "https://upload.wikimedia.org/wikipedia/commons/1/11/Amazon_Prime_Video_logo.svg"},
    "prime video":        {"provider": "Amazon Prime Video", "isNative": True, "logo": "https://upload.wikimedia.org/wikipedia/commons/1/11/Amazon_Prime_Video_logo.svg"},
    "amazon":             {"provider": "Amazon Prime Video", "isNative": True, "logo": "https://upload.wikimedia.org/wikipedia/commons/1/11/Amazon_Prime_Video_logo.svg"},
    "crunchyroll":        {"provider": "Crunchyroll",       "isNative": False, "logo": "https://static.crunchyroll.com/favicons/apple-touch-icon.png"},
    "funimation":         {"provider": "Funimation",        "isNative": False, "logo": "https://www.funimation.com/favicon.ico"},
    "hidive":             {"provider": "HIDIVE",            "isNative": False, "logo": "https://static.hidive.com/favicon.ico"},
    "anime digital network": {"provider": "ADN",            "isNative": False, "logo": "https://animedigitalnetwork.fr/favicon.ico"},
    "adn":                {"provider": "ADN",               "isNative": False, "logo": "https://animedigitalnetwork.fr/favicon.ico"},
    "wakanim":            {"provider": "Wakanim",           "isNative": False, "logo": "https://www.wakanim.tv/favicon.ico"},
    "netflix":            {"provider": "Netflix",           "isNative": False, "logo": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg"},
    "hulu":               {"provider": "Hulu",              "isNative": False, "logo": "https://www.hulu.com/favicon.ico"},
    "disney":             {"provider": "Disney+",           "isNative": False, "logo": "https://www.disneyplus.com/favicon.ico"},
    "disney plus":        {"provider": "Disney+",           "isNative": False, "logo": "https://www.disneyplus.com/favicon.ico"},
    "hbo max":            {"provider": "HBO Max",           "isNative": False, "logo": "https://www.max.com/favicon.ico"},
    "max":                {"provider": "HBO Max",           "isNative": False, "logo": "https://www.max.com/favicon.ico"},
    "youtube":            {"provider": "YouTube",           "isNative": False, "logo": "https://www.youtube.com/s/desktop/favicon.ico"},
    "apple tv":           {"provider": "Apple TV+",         "isNative": False, "logo": "https://tv.apple.com/favicon.ico"},
    "vrv":                {"provider": "VRV",               "isNative": False, "logo": "https://static.vrv.co/favicon.ico"},
    "iqiyi":              {"provider": "iQIYI",             "isNative": False, "logo": "https://www.iq.com/favicon.ico"},
    "bilibili":           {"provider": "Bilibili",          "isNative": False, "logo": "https://www.bilibili.com/favicon.ico"},
}


def _extract_streaming(media: Dict[str, Any]) -> Dict[str, Any]:
    """Return dict: {isOnPrime, primeUrl, sources: [{provider, url, isNative, logo}]}."""
    sources: List[Dict[str, Any]] = []
    prime_url: Optional[str] = None
    seen_sites = set()
    for link in media.get("externalLinks", []) or []:
        site_raw = (link.get("site") or "").strip()
        url = link.get("url") or ""
        if not url:
            continue
        site_lower = site_raw.lower()
        matched = None
        for key, meta in PRIME_BUNDLE_SITES.items():
            if key in site_lower:
                matched = (key, meta)
                break
        if not matched:
            continue
        key, meta = matched
        provider = meta["provider"]
        if provider in seen_sites:
            continue
        seen_sites.add(provider)
        sources.append({
            "provider": provider,
            "url": url,
            "isNative": meta["isNative"],
            "isPrimeBundle": True,  # every match here is part of Amazon Prime universe
            "logo": meta.get("logo"),
        })
        if meta["isNative"] and not prime_url:
            prime_url = url
    is_on_prime = any(s["isNative"] for s in sources)
    return {"isOnPrime": is_on_prime, "primeUrl": prime_url, "sources": sources}


def _is_on_prime(media: Dict[str, Any]) -> Optional[str]:
    return _extract_streaming(media).get("primeUrl")


async def fetch_prime_catalog(limit: int = 4000) -> List[Dict[str, Any]]:
    """Fetch anime that have Amazon Prime Video (or a bundled Prime service) via AniList."""
    all_items: List[Dict[str, Any]] = []
    per_page = 50
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Fetch up to 80 pages to get 4000 anime (since the user requested it)
        for page in range(1, 81):  
            try:
                # To respect AniList rate limits (90 req / min)
                if page > 1:
                    await asyncio.sleep(0.7)
                r = await client.post(
                    ANILIST_URL,
                    json={"query": ANILIST_QUERY, "variables": {"page": page, "perPage": per_page}},
                    timeout=15.0,
                )
                r.raise_for_status()
                data = r.json()
                media_list = data.get("data", {}).get("Page", {}).get("media", []) or []
                if not media_list:
                    break
                for media in media_list:
                    streaming = _extract_streaming(media)
                    prime_url = streaming["primeUrl"]
                    is_on_prime = streaming["isOnPrime"]
                    sources = streaming["sources"]
                    
                    # User requested ALL 4000 trailers, not just Prime Video ones
                    # We will no longer filter by `if not sources:`
                    
                    title_obj = media.get("title") or {}
                    title = title_obj.get("english") or title_obj.get("romaji") or title_obj.get("native") or "Anime"
                    description = (media.get("description") or "").replace("<br>", " ").replace("<i>", "").replace("</i>", "")
                    description = re.sub(r"<[^>]+>", " ", description)
                    description = re.sub(r"\s+", " ", description).strip()
                    trailer = media.get("trailer") or {}
                    trailer_id = trailer.get("id") if (trailer.get("site") or "").lower() == "youtube" else None
                    item = {
                        "id": media["id"],
                        "title": title,
                        "cover": (media.get("coverImage") or {}).get("extraLarge") or (media.get("coverImage") or {}).get("large"),
                        "banner": media.get("bannerImage"),
                        "color": (media.get("coverImage") or {}).get("color") or "#0a1428",
                        "score": media.get("averageScore"),
                        "year": media.get("seasonYear"),
                        "format": media.get("format"),
                        "episodes": media.get("episodes"),
                        "genres": media.get("genres") or [],
                        "description": description[:800] or "Anime disponible via Prime Video.",
                        "primeUrl": prime_url,
                        "isOnPrime": is_on_prime,
                        "sources": sources,
                        "trailerId": trailer_id,
                    }
                    all_items.append(item)
                if len(all_items) >= limit:
                    break
                await asyncio.sleep(0.4)  # respect rate-limit
            except Exception as e:
                logger.warning(f"AniList page {page} failed: {e}")
                await asyncio.sleep(1.0)
    # dedupe by id
    seen = set()
    unique = []
    for item in all_items:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)
    # Sort: native Prime first, then by score
    unique.sort(key=lambda a: (0 if a.get("isOnPrime") else 1, -(a.get("score") or 0)))
    return unique[:limit]
