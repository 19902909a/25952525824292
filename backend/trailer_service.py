
import asyncio
import logging
import re
import time
import httpx
from datetime import datetime, timezone
import os
import feedparser

logger = logging.getLogger(__name__)

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# Broad per-region searches; each result is then classified into an accurate
# version bucket (VO / VOSTFR / VF / EN sub / EN dub) from its title + channel.
YT_SEARCH_RECIPES = [
    ("{t} anime bande annonce VOSTFR VF", "FR", "fr"),
    ("{t} anime english dub sub official trailer", "US", "en"),
    ("{t} アニメ 予告編 PV", "JP", "ja"),
]

# Channel hints used to disambiguate the real version of a trailer.
FR_CHANNELS = ("crunchyroll fr", "adn", "animation digital network", "wakanim", "@nimeland")
EN_CHANNELS = ("muse asia", "ani-one", "anione", "viz media", "netflix anime", "hidive",
               "crunchyroll collection", "crunchyroll dubs", "toonami")
JP_CHANNELS = ("toho animation", "aniplex", "kadokawa", "pony canyon", "kyoani", "bandai",
               "avex pictures", "shueisha")

VERSION_LABELS = {
    "vf": "Français (VF · doublage)",
    "vostfr": "VOSTFR (VO + s-t FR)",
    "vo": "VO (Japonais)",
    "ensub": "English (VO + subs)",
    "endub": "English Dub",
}
# Order of preference for a French-first audience.
VERSION_ORDER = ["vostfr", "vf", "vo", "ensub", "endub"]

# When the daily quota is exhausted, stop calling the API for a while so we
# don't waste requests or spam logs; we serve cached/RSS results meanwhile.
_QUOTA_BLOCKED_UNTIL = 0.0


def _has_japanese(s: str) -> bool:
    return any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in s)


def classify_versions(candidates: list) -> dict:
    """Assign each candidate video to the correct version bucket based on its
    title and source channel, so we never mislabel an English-subtitled trailer
    as the French version."""
    groups = {"vf": [], "vostfr": [], "vo": [], "ensub": [], "endub": []}
    for c in candidates or []:
        vid = c.get("id")
        if not vid:
            continue
        t = (c.get("title") or "").lower()
        src = (c.get("source") or "").lower()
        words = re.findall(r"[a-zà-ÿ]+", t)

        fr_channel = any(ch in src for ch in FR_CHANNELS)
        en_channel = any(ch in src for ch in EN_CHANNELS)
        jp_channel = any(ch in src for ch in JP_CHANNELS)

        is_vf = (("vf" in words or "vff" in words or "doublage" in t
                  or "version française" in t or "version francaise" in t)
                 and "vostfr" not in t and "vost" not in t
                 and "english" not in t and "eng" not in words)
        is_vostfr = ("vostfr" in t or "vost fr" in t or "vost-fr" in t
                     or "sous-titr" in t or "sous titr" in t
                     or (fr_channel and ("english" not in t and "eng sub" not in t)))
        is_endub = ("english dub" in t or "eng dub" in t or "(dub)" in t or " dub " in f" {t} "
                    or "dub)" in t or (en_channel and "dub" in t))
        is_ensub = ("english sub" in t or "eng sub" in t or "subtitle" in t or "(sub)" in t
                    or "english" in t)
        is_vo = (_has_japanese(t) or "予告" in t or "pv" in words or "本編" in t or jp_channel)

        if is_vf:
            bucket = "vf"
        elif is_vostfr:
            bucket = "vostfr"
        elif is_endub:
            bucket = "endub"
        elif is_ensub or en_channel:
            bucket = "ensub"
        elif is_vo:
            bucket = "vo"
        else:
            # Unknown language cues: treat as generic English-subbed original.
            bucket = "ensub"

        if not any(v["id"] == vid for v in groups[bucket]):
            groups[bucket].append({
                "id": vid,
                "title": c.get("title", ""),
                "source": c.get("source", ""),
            })

    return {k: v[:5] for k, v in groups.items() if v}


def _flatten_cached(doc: dict) -> list:
    """Return a flat candidate list from a cache doc (new 'candidates' format or
    the legacy 'results' grouped format)."""
    if not doc:
        return []
    if doc.get("candidates"):
        return doc["candidates"]
    out = []
    for _lang, items in (doc.get("results") or {}).items():
        for it in items or []:
            if isinstance(it, str):
                out.append({"id": it, "title": "", "source": ""})
            elif isinstance(it, dict) and it.get("id"):
                out.append({"id": it["id"], "title": it.get("title", ""), "source": it.get("source", "")})
    return out


async def _yt_dlp_search(q: str, max_results: int = 6) -> list:
    def _search():
        from yt_dlp import YoutubeDL
        opts = {"quiet": True, "extract_flat": True, "force_generic_extractor": True}
        try:
            with YoutubeDL(opts) as ydl:
                res = ydl.extract_info(f"ytsearch{max_results}:{q}", download=False)
                return res.get("entries", [])
        except Exception as e:
            logger.warning(f"yt-dlp search failed: {e}")
            return []
    return await asyncio.to_thread(_search)

async def youtube_search_multilang(title: str, db=None) -> dict:
    """Return real, embeddable trailers grouped by ACCURATE version
    (vo / vostfr / vf / ensub / endub) using yt-dlp to bypass API limits. Raw
    candidates are cached in Mongo so even previously cached data is labelled correctly."""
    if not title:
        return {}

    series_key = normalize_title(title) or title.strip().lower()
    if len(series_key) < 2:
        series_key = title.strip().lower()

    # 1) Cache lookup (classify at read time — fixes any previously mislabeled data)
    if db is not None:
        try:
            cached = await db.trailer_cache.find_one({"series_key": series_key})
            candidates = _flatten_cached(cached)
            if candidates:
                return classify_versions(candidates)
        except Exception as e:
            logger.warning(f"trailer_cache lookup failed: {e}")

    candidates: list = []
    seen = set()
    
    for tmpl, region, rel in YT_SEARCH_RECIPES:
        q = tmpl.format(t=title)
        entries = await _yt_dlp_search(q, max_results=6)
        for it in entries:
            vid = it.get("id")
            if vid and vid not in seen:
                seen.add(vid)
                candidates.append({
                    "id": vid,
                    "title": it.get("title", ""),
                    "source": it.get("uploader", "YouTube"),
                })
        await asyncio.sleep(0.5)

    # 2) Persist raw candidates
    if db is not None and candidates:
        try:
            await db.trailer_cache.replace_one(
                {"series_key": series_key},
                {"series_key": series_key, "candidates": candidates, "cached_at": datetime.now(timezone.utc)},
                upsert=True,
            )
        except Exception as e:
            logger.warning(f"trailer_cache persist failed: {e}")

    return classify_versions(candidates)


# Expanded list of official anime channels to scan for multilingual trailers
OFFICIAL_CHANNELS = [
    # French
    {"lang": "fr", "id": "UCqwZ2X12hR3r983l-D5B41w", "name": "Crunchyroll FR"},
    {"lang": "fr", "id": "UC5H9qX05T28W3H4R8GqD8qA", "name": "ADN - Animation Digital Network"},
    {"lang": "fr", "id": "UCDxG1h_sW-0mF3xU5h3cO8g", "name": "Wakanim FR"},
    # English
    {"lang": "en", "id": "UCtXIw-uKzF_LndYwAWBf6TQ", "name": "Crunchyroll Collection"},
    {"lang": "en", "id": "UCUxg-n1n6mN3P2B1F_QW_lQ", "name": "Viz Media"},
    {"lang": "en", "id": "UC8cgOWQEXkRofI4yW_w6-ag", "name": "Netflix Anime"},
    {"lang": "en", "id": "UCnHMhLnt2FqAOr87R27N-bQ", "name": "Crunchyroll Dubs"}, # Actually CR Dubs channel exists
    {"lang": "en", "id": "UCqly9F4Fr_jf2Y1Cy5hacRg", "name": "Ani-One Asia"},
    {"lang": "en", "id": "UCGbshtvS9t-8CW11W7TooQg", "name": "Muse Asia"},
    {"lang": "en", "id": "UC0W2sPZz8O7I43bZqJ-jA0g", "name": "HIDIVE"},
    # Spanish
    {"lang": "es", "id": "UCnHMhLnt2FqAOr87R27N-bQ", "name": "Crunchyroll en Español"},
    # German
    {"lang": "de", "id": "UC0t-wD1D4xQo5Fv5R3jA9aA", "name": "Crunchyroll Deutschland"},
    # Portuguese
    {"lang": "pt", "id": "UCb3K02X4tN9m2K2MhM430TQ", "name": "Crunchyroll PT"},
    # Japanese
    {"lang": "ja", "id": "UC1oPBUWifc0QOOY8DEKhLuQ", "name": "TOHO animation"},
    {"lang": "ja", "id": "UCp-5t9CxOWEU9HXQEIeBpzg", "name": "KADOKAWAanime"},
    {"lang": "ja", "id": "UCeOMz8AyCGHMtpKlFSUes-Q", "name": "Aniplex"},
    {"lang": "ja", "id": "UCQ2_y3rC8D-W9q20wFw7o2A", "name": "KyoaniChannel"},
    {"lang": "ja", "id": "UCW7J7hSgC5-9iX5kI2jTz4Q", "name": "Pony Canyon"},
]

def normalize_title(title: str) -> str:
    """Extract base series name from a trailer title."""
    clean = re.sub(r'(?i)(trailer|bande annonce|teaser|official|offiziell|pv|preview|vf|vostfr|sub|dub|opening|ending|cour|season|saison|\#\d+)', '', title)
    clean = re.sub(r'\[.*?\]|\(.*?\)', '', clean)
    clean = re.split(r'\||\-', clean)[0]
    return clean.strip().lower()

async def sync_multilingual_trailers(db=None):
    """Background task to fetch latest trailers from official channels every 2 hours."""
    while True:
        try:
            logger.info("Starting extensive multilingual trailer sync...")
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                for ch in OFFICIAL_CHANNELS:
                    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
                    try:
                        r = await client.get(url)
                        if r.status_code == 200:
                            feed = feedparser.parse(r.text)
                            for entry in feed.entries:
                                yt_id = entry.get("yt_videoid", "")
                                if not yt_id:
                                    continue
                                
                                title = entry.get("title", "")
                                series_key = normalize_title(title)
                                
                                if not series_key or len(series_key) < 3:
                                    continue
                                
                                doc = {
                                    "yt_id": yt_id,
                                    "title": title,
                                    "series_key": series_key,
                                    "lang": ch["lang"],
                                    "source": ch["name"],
                                    "published_at": entry.get("published", ""),
                                    "fetched_at": datetime.now(timezone.utc)
                                }
                                
                                if db is not None:
                                    await db.trailers.update_one(
                                        {"yt_id": yt_id},
                                        {"$set": doc},
                                        upsert=True
                                    )
                    except Exception as e:
                        logger.warning(f"Failed to fetch trailers from {ch['name']}: {e}")
            
            logger.info("Multilingual trailer sync complete.")
        except Exception as e:
            logger.error(f"Error in trailer sync loop: {e}")
            
        # Run autonomously every 2 hours
        await asyncio.sleep(7200)

async def get_trailers_for_series(series_name: str, db):
    """Find the best matching trailers for a given series name from DB."""
    norm_search = normalize_title(series_name)
    if len(norm_search) < 3:
        return {}
        
    # Search by exact series_key or regex
    cursor = db.trailers.find({
        "$or": [
            {"series_key": norm_search},
            {"series_key": {"$regex": norm_search, "$options": "i"}}
        ]
    })
    
    results = await cursor.to_list(length=100)
    
    # Group by language
    grouped = {}
    for doc in results:
        lang = doc["lang"]
        if lang not in grouped:
            grouped[lang] = []
        
        # Don't add duplicates
        if not any(v["id"] == doc["yt_id"] for v in grouped[lang]):
            grouped[lang].append({
                "id": doc["yt_id"],
                "title": doc["title"],
                "source": doc["source"]
            })
            
    # Add some hardcoded fallbacks just in case the db hasn't synced yet
    if "jujutsu kaisen" in norm_search:
        if "fr" not in grouped: grouped["fr"] = [{"id": "MGRm4IzK1SQ", "title": "Jujutsu Kaisen VF", "source": "Crunchyroll FR"}]
    elif "demon slayer" in norm_search:
        if "fr" not in grouped: grouped["fr"] = [{"id": "KKzZ2mPS3jU", "title": "Demon Slayer VF", "source": "Crunchyroll FR"}]
        
    return grouped
