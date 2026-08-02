import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from trailer_service import normalize_title

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    base = await db.trailer_cache.find_one({"series_key": "frieren"})
    if not base or not base.get("results"):
        print("No base 'frieren' cache found; nothing to alias.")
        return
    results = base["results"]
    aliases = [
        "Frieren: Beyond Journey’s End",
        "Frieren: Beyond Journey's End",
        "Sousou no Frieren",
        "Frieren: Beyond Journey’s End Season 2",
        "Frieren: Beyond Journey's End Season 2",
        "Sousou no Frieren Season 2",
    ]
    for title in aliases:
        key = normalize_title(title) or title.strip().lower()
        await db.trailer_cache.replace_one(
            {"series_key": key},
            {"series_key": key, "results": results, "cached_at": datetime.now(timezone.utc)},
            upsert=True,
        )
        print(f"Aliased '{title}' -> series_key='{key}' with langs {list(results.keys())}")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
