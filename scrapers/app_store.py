from app_store_scraper import AppStore
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SPOTIFY_APP_ID_IOS


def scrape_app_store(days: int = 30, max_reviews: int = 500) -> list[dict]:
    print(f"[App Store] Scraping last {days} days...")
    cutoff = datetime.now() - timedelta(days=days)

    app = AppStore(country="us", app_name="spotify-music", app_id=SPOTIFY_APP_ID_IOS)
    app.review(how_many=max_reviews)

    reviews = []
    for r in app.reviews:
        date = r.get("date")
        if isinstance(date, datetime) and date < cutoff:
            continue
        reviews.append({
            "source": "app_store",
            "platform": "ios",
            "text": r.get("review", ""),
            "rating": r.get("rating"),
            "date": date.isoformat() if isinstance(date, datetime) else str(date),
            "user_id": r.get("userName", ""),
            "title": r.get("title", ""),
        })

    print(f"[App Store] {len(reviews)} reviews collected")
    return reviews
