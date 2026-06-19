import json
import os
import uuid
from datetime import datetime
from pipeline.prefilter import filter_reviews
from pipeline.storage import init_db, save_reviews, save_run
from config import OUTPUTS_DIR, RAW_DIR


def run_ingestion(sources: list[str], days: int, progress_callback=None) -> dict:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    started_at = datetime.now().isoformat()

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    init_db()

    def update(msg):
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)

    all_raw = []

    if "app_store" in sources:
        update("scraping_app_store")
        try:
            from scrapers.app_store import scrape_app_store
            reviews = scrape_app_store(days=days)
            all_raw.extend(reviews)
            update(f"app_store_done:{len(reviews)}")
        except Exception as e:
            update(f"app_store_error:{e}")

    if "play_store" in sources:
        update("scraping_play_store")
        try:
            from scrapers.play_store import scrape_play_store
            reviews = scrape_play_store(days=days)
            all_raw.extend(reviews)
            update(f"play_store_done:{len(reviews)}")
        except Exception as e:
            update(f"play_store_error:{e}")

    if "reddit" in sources:
        update("scraping_reddit")
        try:
            from scrapers.reddit_scraper import scrape_reddit
            reviews = scrape_reddit(days=days)
            all_raw.extend(reviews)
            update(f"reddit_done:{len(reviews)}")
        except Exception as e:
            update(f"reddit_error:{e}")

    if "community" in sources:
        update("scraping_community")
        try:
            from scrapers.community_scraper import scrape_community
            reviews = scrape_community(days=days)
            all_raw.extend(reviews)
            update(f"community_done:{len(reviews)}")
        except Exception as e:
            update(f"community_error:{e}")

    with open(f"{RAW_DIR}/raw_{run_id}.json", "w") as f:
        json.dump(all_raw, f, indent=2)

    update("filtering")
    clean_reviews, filter_log = filter_reviews(all_raw)

    update("saving")
    save_reviews(clean_reviews, run_id)

    completed_at = datetime.now().isoformat()
    save_run(
        run_id=run_id,
        started_at=started_at,
        completed_at=completed_at,
        sources=sources,
        days=days,
        total_raw=len(all_raw),
        total_filtered=filter_log["total_raw"] - filter_log["passed"],
        total_clean=filter_log["passed"],
        filter_log=filter_log,
        status="completed",
    )

    result = {
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": completed_at,
        "sources": sources,
        "days": days,
        "total_raw": len(all_raw),
        "total_clean": filter_log["passed"],
        "filter_log": filter_log,
    }

    out_dir = f"{OUTPUTS_DIR}/{run_id}"
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/filter_log.json", "w") as f:
        json.dump(result, f, indent=2)

    update(f"done:{run_id}")
    return result
