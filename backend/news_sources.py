"""
50 real RSS/API news sources for anime, manga, streaming, gaming and Japanese pop culture.
Each source has an ID, name, category, RSS URL, language and region.
"""

NEWS_SOURCES = [
    # === ANIME (French) ===
    {"id": "anime-news-network-fr", "name": "Anime News Network FR", "source_group": "Anime News Network", "categories": ["anime", "manga"], "rss": "https://www.animenewsnetwork.com/newsroom/rss.xml", "site_url": "https://www.animenewsnetwork.com", "language": "en", "region": "global", "priority": 10},
    {"id": "manga-news", "name": "Manga News", "source_group": "Manga News", "categories": ["manga", "anime"], "rss": "https://www.manga-news.com/index.php/feed/actus", "site_url": "https://www.manga-news.com", "language": "fr", "region": "fr", "priority": 9},
    {"id": "adala-news", "name": "Adala News", "source_group": "Adala News", "categories": ["anime", "manga"], "rss": "https://adala-news.fr/feed/", "site_url": "https://adala-news.fr", "language": "fr", "region": "fr", "priority": 9},
    {"id": "anime-otaku", "name": "Anime Otaku", "source_group": "Anime Otaku", "categories": ["anime"], "rss": "https://www.animeotaku.fr/feed/", "site_url": "https://www.animeotaku.fr", "language": "fr", "region": "fr", "priority": 7},
    {"id": "planete-jeunesse", "name": "Planète Jeunesse", "source_group": "Planète Jeunesse", "categories": ["anime"], "rss": "https://www.planete-jeunesse.com/rss/actus.xml", "site_url": "https://www.planete-jeunesse.com", "language": "fr", "region": "fr", "priority": 6},
    {"id": "nautiljon", "name": "Nautiljon", "source_group": "Nautiljon", "categories": ["anime", "manga", "pop-culture"], "rss": "https://www.nautiljon.com/rss/news.xml", "site_url": "https://www.nautiljon.com", "language": "fr", "region": "fr", "priority": 9},
    {"id": "otakugame", "name": "OtakuGame", "source_group": "OtakuGame", "categories": ["anime", "gaming"], "rss": "https://otakugame.fr/feed/", "site_url": "https://otakugame.fr", "language": "fr", "region": "fr", "priority": 7},
    {"id": "coyote-mag", "name": "Coyote Mag", "source_group": "Coyote Mag", "categories": ["manga", "anime"], "rss": "https://www.coyotemag.fr/feed/", "site_url": "https://www.coyotemag.fr", "language": "fr", "region": "fr", "priority": 6},
    {"id": "mangamag", "name": "Manga Mag", "source_group": "Manga Mag", "categories": ["manga"], "rss": "https://www.mangamag.fr/feed/", "site_url": "https://www.mangamag.fr", "language": "fr", "region": "fr", "priority": 6},

    # === ANIME/MANGA (English/Global) ===
    {"id": "crunchyroll-news", "name": "Crunchyroll News", "source_group": "Crunchyroll", "categories": ["anime", "streaming"], "rss": "https://www.crunchyroll.com/newsrss", "site_url": "https://www.crunchyroll.com", "language": "en", "region": "global", "priority": 10},
    {"id": "anime-uk-news", "name": "Anime UK News", "source_group": "Anime UK News", "categories": ["anime", "manga"], "rss": "https://animeuknews.net/feed/", "site_url": "https://animeuknews.net", "language": "en", "region": "uk", "priority": 7},
    {"id": "comic-book-resources-anime", "name": "CBR Anime", "source_group": "CBR", "categories": ["anime", "manga"], "rss": "https://www.cbr.com/feed/category/anime-news/", "site_url": "https://www.cbr.com", "language": "en", "region": "global", "priority": 8},
    {"id": "otaquest", "name": "OTAQUEST", "source_group": "OTAQUEST", "categories": ["anime", "pop-culture"], "rss": "https://www.otaquest.com/feed/", "site_url": "https://www.otaquest.com", "language": "en", "region": "global", "priority": 7},
    {"id": "japan-today-arts", "name": "Japan Today Arts", "source_group": "Japan Today", "categories": ["pop-culture", "anime"], "rss": "https://japantoday.com/feed?category=entertainment", "site_url": "https://japantoday.com", "language": "en", "region": "jp", "priority": 8},
    {"id": "kotaku-anime", "name": "Kotaku", "source_group": "Kotaku", "categories": ["gaming", "anime"], "rss": "https://kotaku.com/rss", "site_url": "https://kotaku.com", "language": "en", "region": "global", "priority": 9},
    {"id": "anime-hunch", "name": "Anime Hunch", "source_group": "Anime Hunch", "categories": ["anime"], "rss": "https://animehunch.com/feed/", "site_url": "https://animehunch.com", "language": "en", "region": "global", "priority": 6},
    {"id": "anime-corner", "name": "Anime Corner", "source_group": "Anime Corner", "categories": ["anime"], "rss": "https://animecorner.me/feed/", "site_url": "https://animecorner.me", "language": "en", "region": "global", "priority": 7},
    {"id": "anime-motivation", "name": "Anime Motivation", "source_group": "Anime Motivation", "categories": ["anime", "pop-culture"], "rss": "https://animemotivation.com/feed/", "site_url": "https://animemotivation.com", "language": "en", "region": "global", "priority": 5},
    {"id": "anime-trending", "name": "Anime Trending", "source_group": "Anime Trending", "categories": ["anime"], "rss": "https://www.animetrending.net/feed/", "site_url": "https://www.animetrending.net", "language": "en", "region": "global", "priority": 6},

    # === STREAMING ===
    {"id": "netflix-tudum", "name": "Netflix Tudum", "source_group": "Netflix", "categories": ["streaming", "anime"], "rss": "https://about.netflix.com/en/newsroom/rss.xml", "site_url": "https://www.netflix.com", "language": "en", "region": "global", "priority": 8},
    {"id": "variety-tv", "name": "Variety TV", "source_group": "Variety", "categories": ["streaming", "pop-culture"], "rss": "https://variety.com/v/tv/feed/", "site_url": "https://variety.com", "language": "en", "region": "us", "priority": 8},

    # === GAMING ===
    {"id": "millenium-jv", "name": "Millenium", "source_group": "Millenium", "categories": ["gaming"], "rss": "https://www.millenium.org/news/feed", "site_url": "https://www.millenium.org", "language": "fr", "region": "fr", "priority": 7},
    {"id": "gameblog", "name": "Gameblog", "source_group": "Gameblog", "categories": ["gaming"], "rss": "https://www.gameblog.fr/rss/news", "site_url": "https://www.gameblog.fr", "language": "fr", "region": "fr", "priority": 7},
    {"id": "ign-fr", "name": "IGN France", "source_group": "IGN", "categories": ["gaming", "streaming"], "rss": "https://fr.ign.com/feed.xml", "site_url": "https://fr.ign.com", "language": "fr", "region": "fr", "priority": 9},
    {"id": "ign-en", "name": "IGN", "source_group": "IGN", "categories": ["gaming"], "rss": "https://feeds.ign.com/ign/all", "site_url": "https://www.ign.com", "language": "en", "region": "global", "priority": 9},
    {"id": "gamespot", "name": "GameSpot", "source_group": "GameSpot", "categories": ["gaming"], "rss": "https://www.gamespot.com/feeds/mashup/", "site_url": "https://www.gamespot.com", "language": "en", "region": "global", "priority": 8},
    {"id": "polygon", "name": "Polygon", "source_group": "Polygon", "categories": ["gaming", "anime"], "rss": "https://www.polygon.com/rss/index.xml", "site_url": "https://www.polygon.com", "language": "en", "region": "global", "priority": 8},
    {"id": "eurogamer", "name": "Eurogamer", "source_group": "Eurogamer", "categories": ["gaming"], "rss": "https://www.eurogamer.net/feed", "site_url": "https://www.eurogamer.net", "language": "en", "region": "eu", "priority": 7},

    # === POP CULTURE JAPONAISE ===
    {"id": "sora-news-24", "name": "SoraNews24", "source_group": "SoraNews24", "categories": ["pop-culture", "anime"], "rss": "https://soranews24.com/feed/", "site_url": "https://soranews24.com", "language": "en", "region": "jp", "priority": 8},
    {"id": "japan-times", "name": "The Japan Times", "source_group": "Japan Times", "categories": ["pop-culture"], "rss": "https://www.japantimes.co.jp/feed/", "site_url": "https://www.japantimes.co.jp", "language": "en", "region": "jp", "priority": 8},
    {"id": "tokyo-weekender", "name": "Tokyo Weekender", "source_group": "Tokyo Weekender", "categories": ["pop-culture"], "rss": "https://www.tokyoweekender.com/feed/", "site_url": "https://www.tokyoweekender.com", "language": "en", "region": "jp", "priority": 6},
    {"id": "japan-forward", "name": "Japan Forward", "source_group": "Japan Forward", "categories": ["pop-culture"], "rss": "https://japan-forward.com/feed/", "site_url": "https://japan-forward.com", "language": "en", "region": "jp", "priority": 6},
    {"id": "unseen-japan", "name": "Unseen Japan", "source_group": "Unseen Japan", "categories": ["pop-culture"], "rss": "https://unseenjapan.com/feed/", "site_url": "https://unseenjapan.com", "language": "en", "region": "jp", "priority": 6},
    {"id": "nippon-com", "name": "Nippon.com", "source_group": "Nippon.com", "categories": ["pop-culture"], "rss": "https://www.nippon.com/en/feed/", "site_url": "https://www.nippon.com", "language": "en", "region": "jp", "priority": 7},
    {"id": "asian-boss-japan", "name": "Grape Japan", "source_group": "Grape Japan", "categories": ["pop-culture"], "rss": "https://grapee.jp/en/feed/", "site_url": "https://grapee.jp/en", "language": "en", "region": "jp", "priority": 6},
    {"id": "japan-info", "name": "Japan Info", "source_group": "Japan Info", "categories": ["pop-culture"], "rss": "https://jpninfo.com/feed", "site_url": "https://jpninfo.com", "language": "en", "region": "jp", "priority": 5},
    {"id": "livedoor-anime", "name": "Livedoor Anime News", "source_group": "Livedoor", "categories": ["anime", "pop-culture"], "rss": "https://news.livedoor.com/topics/rss/eco.xml", "site_url": "https://news.livedoor.com", "language": "ja", "region": "jp", "priority": 5},
    {"id": "anime-recorder", "name": "Anime Recorder", "source_group": "Anime Recorder", "categories": ["anime"], "rss": "https://www.animerecorder.com/feed/", "site_url": "https://www.animerecorder.com", "language": "en", "region": "global", "priority": 5},
]
