import requests
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SPOTIFY_APP_ID_IOS

# Apple's public RSS feed — no auth, no library dependency
APP_STORE_RSS = "https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"


def scrape_app_store(days: int = 30, max_reviews: int = 500) -> list[dict]:
    print(f"[App Store] Scraping last {days} days...")
    cutoff = datetime.now() - timedelta(days=days)
    collected = []

    # Apple RSS returns up to 10 pages of 50 reviews each = 500 max
    for page in range(1, 11):
        if len(collected) >= max_reviews:
            break
        try:
            url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={SPOTIFY_APP_ID_IOS}/sortBy=mostRecent/json"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                break

            data = resp.json()
            entries = data.get("feed", {}).get("entry", [])

            if not entries:
                break

            # First entry is app metadata, skip it
            if isinstance(entries, list) and entries:
                entries = entries[1:]

            for entry in entries:
                try:
                    updated = entry.get("updated", {}).get("label", "")
                    date = datetime.fromisoformat(updated[:10]) if updated else datetime.now()

                    if date < cutoff:
                        continue

                    text = entry.get("content", {}).get("label", "").strip()
                    title = entry.get("title", {}).get("label", "")
                    rating = entry.get("im:rating", {}).get("label")
                    author = entry.get("author", {}).get("name", {}).get("label", "")

                    collected.append({
                        "source": "app_store",
                        "platform": "ios",
                        "text": f"{title}. {text}".strip(" .") if title else text,
                        "rating": int(rating) if rating else None,
                        "date": date.isoformat(),
                        "user_id": author,
                        "title": title,
                    })
                except Exception:
                    continue

        except Exception as e:
            print(f"[App Store] Error on page {page}: {e}")
            break

    print(f"[App Store] {len(collected)} reviews collected")
    return collected
