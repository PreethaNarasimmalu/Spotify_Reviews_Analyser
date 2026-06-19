from google_play_scraper import reviews, Sort
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SPOTIFY_PACKAGE_ANDROID


def scrape_play_store(days: int = 30, max_reviews: int = 500) -> list[dict]:
    print(f"[Play Store] Scraping last {days} days...")
    cutoff = datetime.now() - timedelta(days=days)

    result, _ = reviews(
        SPOTIFY_PACKAGE_ANDROID,
        lang="en",
        country="us",
        sort=Sort.NEWEST,
        count=max_reviews,
    )

    collected = []
    for r in result:
        date = r.get("at")
        if isinstance(date, datetime) and date < cutoff:
            continue
        collected.append({
            "source": "play_store",
            "platform": "android",
            "text": r.get("content", ""),
            "rating": r.get("score"),
            "date": date.isoformat() if isinstance(date, datetime) else str(date),
            "user_id": r.get("userName", ""),
            "title": "",
        })

    print(f"[Play Store] {len(collected)} reviews collected")
    return collected
