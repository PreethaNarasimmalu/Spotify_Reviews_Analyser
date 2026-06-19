import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


COMMUNITY_SEARCH_URLS = [
    "https://community.spotify.com/t5/forums/searchpage/tab/message?q=music+discovery&search_type=thread",
    "https://community.spotify.com/t5/forums/searchpage/tab/message?q=recommendations&search_type=thread",
    "https://community.spotify.com/t5/forums/searchpage/tab/message?q=same+songs&search_type=thread",
    "https://community.spotify.com/t5/forums/searchpage/tab/message?q=discover+weekly&search_type=thread",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def scrape_community(days: int = 30, max_threads: int = 50) -> list[dict]:
    print(f"[Community] Scraping last {days} days...")
    collected = []

    for url in COMMUNITY_SEARCH_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"[Community] Status {resp.status_code} for {url}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            posts = soup.find_all("div", class_="lia-message-body-content")

            for post in posts[:max_threads // len(COMMUNITY_SEARCH_URLS)]:
                text = post.get_text(separator=" ", strip=True)
                if not text:
                    continue
                collected.append({
                    "source": "community",
                    "platform": "community",
                    "text": text,
                    "rating": None,
                    "date": datetime.now().isoformat(),
                    "user_id": "",
                    "title": "",
                })

            time.sleep(1)

        except Exception as e:
            print(f"[Community] Error: {e}")
            continue

    print(f"[Community] {len(collected)} posts collected")
    return collected
