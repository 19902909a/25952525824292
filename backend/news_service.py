"""
News aggregator service: fetches RSS from 50 real sources,
normalizes, scores and caches items in MongoDB.
"""
import asyncio
import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import httpx

from news_sources import NEWS_SOURCES

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(8.0, connect=5.0)
CONCURRENCY = 12
FALLBACK_IMAGE = "/lovanet-og.svg"


def _slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    text = re.sub(r"\s+", "-", text.strip())
    return text[:120] or hashlib.md5(text.encode()).hexdigest()[:16]


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_image(entry: Any) -> Optional[str]:
    # media:content / media:thumbnail
    if getattr(entry, "media_content", None):
        for m in entry.media_content:
            if m.get("url"):
                return m["url"]
    if getattr(entry, "media_thumbnail", None):
        for m in entry.media_thumbnail:
            if m.get("url"):
                return m["url"]
    # enclosures
    for enc in entry.get("enclosures", []) or []:
        if enc.get("type", "").startswith("image") and enc.get("href"):
            return enc["href"]
    # image tags in content
    content_html = ""
    if entry.get("content"):
        content_html = entry.content[0].get("value", "")
    content_html = content_html or entry.get("summary", "") or entry.get("description", "")
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html)
    if match:
        return match.group(1)
    return None


def _parse_date(entry: Any) -> str:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                struct = entry.get(f"{key}_parsed")
                if struct:
                    dt = datetime(*struct[:6], tzinfo=timezone.utc)
                    return dt.isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def _trending_score(published_iso: str, priority: int, keywords: List[str]) -> float:
    try:
        published = datetime.fromisoformat(published_iso.replace("Z", "+00:00"))
    except Exception:
        published = datetime.now(timezone.utc)
    hours = max(0.1, (datetime.now(timezone.utc) - published).total_seconds() / 3600)
    freshness = max(0.0, 96.0 - hours) / 96.0  # 0..1
    kw_boost = min(1.0, len(keywords) / 6.0)
    return round((priority * 6.5) + (freshness * 45) + (kw_boost * 12), 2)


async def _fetch_one(client: httpx.AsyncClient, source: Dict[str, Any]) -> Dict[str, Any]:
    result = {"source": source, "items": [], "error": None, "count": 0, "fetched_at": datetime.now(timezone.utc).isoformat()}
    try:
        response = await client.get(source["rss"], timeout=DEFAULT_TIMEOUT, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; LovanetNewsBot/1.0)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9,*/*;q=0.8",
        })
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        for entry in feed.entries[:20]:
            title = _strip_html(entry.get("title", "")).strip()
            link = entry.get("link") or ""
            if not title or not link:
                continue
            description = _strip_html(entry.get("summary") or entry.get("description") or "")
            content_html = ""
            if entry.get("content"):
                content_html = entry.content[0].get("value", "")
            content_text = _strip_html(content_html) or description
            published_iso = _parse_date(entry)
            image = _extract_image(entry)
            slug_base = f"{source['id']}-{_slugify(title)}"
            slug = slug_base[:140]
            categories = source.get("categories", [])
            tags = [t.get("term") for t in entry.get("tags", []) if t.get("term")]
            item = {
                "id": hashlib.md5(link.encode()).hexdigest(),
                "slug": slug,
                "title": title,
                "description": description[:400],
                "excerpt": description[:280],
                "content": content_text[:4000],
                "image": image,
                "published_at": published_iso,
                "source_name": source["name"],
                "source_group": source.get("source_group", source["name"]),
                "source_id": source["id"],
                "source_path": link,
                "source_domain": urlparse(link).netloc,
                "author": entry.get("author") or source["name"],
                "categories": categories,
                "categoryLabels": [c.replace("-", " ").title() for c in categories],
                "tags": (tags or [])[:8],
                "is_breaking": False,
                "is_featured": False,
                "verified": True,
                "trending_score": _trending_score(published_iso, source.get("priority", 5), tags or []),
                "embed_video": None,
                "anime_ref": None,
            }
            result["items"].append(item)
        result["count"] = len(result["items"])
        logger.info(f"Fetched {result['count']} items from {source['id']}")
    except Exception as e:
        result["error"] = str(e)[:200]
        logger.warning(f"Failed to fetch {source['id']}: {e}")
    return result


async def fetch_all_sources() -> Dict[str, Any]:
    """Fetch all sources concurrently. Returns items + source statuses."""
    all_items: List[Dict[str, Any]] = []
    source_statuses: List[Dict[str, Any]] = []
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        async def run(source):
            async with semaphore:
                return await _fetch_one(client, source)
        results = await asyncio.gather(*[run(s) for s in NEWS_SOURCES], return_exceptions=True)

    for res in results:
        if isinstance(res, Exception):
            continue
        source = res["source"]
        source_statuses.append({
            "id": source["id"],
            "name": source["name"],
            "source_group": source.get("source_group", source["name"]),
            "categories": source.get("categories", []),
            "priority": source.get("priority", 5),
            "status": "ok" if res["count"] > 0 else "degraded",
            "last_success_at": res["fetched_at"] if res["count"] > 0 else None,
            "last_count": res["count"],
            "last_error": res["error"],
            "site_url": source.get("site_url"),
            "language": source.get("language", "en"),
            "region": source.get("region", "global"),
        })
        all_items.extend(res["items"])

    # deduplicate by id
    seen = set()
    unique_items = []
    for item in all_items:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique_items.append(item)

    # mark breaking (top 3 highest trending) and featured (top 8)
    unique_items.sort(key=lambda x: x["trending_score"], reverse=True)
    for i, item in enumerate(unique_items[:3]):
        item["is_breaking"] = True
    for item in unique_items[:8]:
        item["is_featured"] = True

    return {
        "items": unique_items,
        "sources": source_statuses,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_home(items: List[Dict[str, Any]], sources: List[Dict[str, Any]], updated_at: str) -> Dict[str, Any]:
    """Structure items for the /api/news/home payload."""
    by_recent = sorted(items, key=lambda x: x["published_at"], reverse=True)
    by_trending = sorted(items, key=lambda x: x["trending_score"], reverse=True)

    rails: Dict[str, List[Dict[str, Any]]] = {}
    for cat in ["anime", "manga", "streaming", "gaming", "pop-culture"]:
        rails[cat] = [i for i in by_trending if cat in i.get("categories", [])][:12]

    hero = by_trending[:5]
    featured = by_trending[:12]
    latest = by_recent[:24]
    trending = by_trending[:10]
    calendar = [i for i in by_recent if "anime" in i.get("categories", [])][:8]

    return {
        "hero": hero,
        "featured": featured,
        "latest": latest,
        "rails": rails,
        "trending": trending,
        "calendar": calendar,
        "sources": sources,
        "updated_at": updated_at,
    }


def filter_items(
    items: List[Dict[str, Any]],
    category: Optional[str] = None,
    source: Optional[str] = None,
    query: Optional[str] = None,
    sort: str = "trending",
    limit: int = 24,
    offset: int = 0,
) -> Dict[str, Any]:
    filtered = list(items)
    if category and category != "all":
        filtered = [i for i in filtered if category in i.get("categories", [])]
    if source and source != "all":
        filtered = [i for i in filtered if i.get("source_id") == source]
    if query:
        q = query.lower()
        filtered = [
            i for i in filtered
            if q in i["title"].lower()
            or q in (i.get("description") or "").lower()
            or q in " ".join(i.get("tags", [])).lower()
        ]
    if sort == "recent":
        filtered.sort(key=lambda x: x["published_at"], reverse=True)
    else:
        filtered.sort(key=lambda x: x["trending_score"], reverse=True)

    total = len(filtered)
    page = filtered[offset:offset + limit]
    return {
        "items": page,
        "total": total,
        "offset": offset,
        "limit": limit,
        "source": source or "all",
        "categories": [
            {"id": "anime", "label": "Anime"},
            {"id": "manga", "label": "Manga"},
            {"id": "streaming", "label": "Streaming"},
            {"id": "gaming", "label": "Gaming"},
            {"id": "pop-culture", "label": "Pop-culture JP"},
        ],
    }
