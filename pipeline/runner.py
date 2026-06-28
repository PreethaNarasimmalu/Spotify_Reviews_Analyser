import json
import os
import uuid
from datetime import datetime
from pipeline.prefilter import filter_reviews
from pipeline.storage import init_db, save_reviews, save_run
from pipeline.extractor import extract_all
from pipeline.scorer import score_opportunities
from pipeline.synthesizer import synthesize
from config import OUTPUTS_DIR, RAW_DIR


def run_pipeline(sources: list[str], days: int, progress_callback=None) -> dict:
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

    # ── Phase 1: Scraping ─────────────────────────────────────────────
    all_raw = []

    if "app_store" in sources:
        update("scraping_app_store")
        try:
            from scrapers.app_store import scrape_app_store
            r = scrape_app_store(days=days)
            all_raw.extend(r)
            update(f"app_store_done:{len(r)}")
        except Exception as e:
            update(f"app_store_error:{e}")

    if "play_store" in sources:
        update("scraping_play_store")
        try:
            from scrapers.play_store import scrape_play_store
            r = scrape_play_store(days=days)
            all_raw.extend(r)
            update(f"play_store_done:{len(r)}")
        except Exception as e:
            update(f"play_store_error:{e}")

    if "community" in sources:
        update("scraping_community")
        try:
            from scrapers.community_scraper import scrape_community
            r = scrape_community(days=days)
            all_raw.extend(r)
            update(f"community_done:{len(r)}")
        except Exception as e:
            update(f"community_error:{e}")

    with open(f"{RAW_DIR}/raw_{run_id}.json", "w") as f:
        json.dump(all_raw, f, indent=2)

    # ── Phase 1: Pre-filter ───────────────────────────────────────────
    update("filtering")
    clean_reviews, filter_log = filter_reviews(all_raw)
    update(f"filtered:{filter_log['passed']}/{filter_log['total_raw']}")

    save_reviews(clean_reviews, run_id)

    # ── Phase 2: AI Extraction (Groq) ─────────────────────────────────
    update("extracting")
    enriched = extract_all(clean_reviews, batch_size=20, progress_callback=update)
    update(f"extraction_done:{len(enriched)}")

    # ── Phase 2: Opportunity Scoring ──────────────────────────────────
    update("scoring")
    clusters = score_opportunities(enriched)
    update(f"scoring_done:{len(clusters)}")

    # ── Phase 2: Claude Synthesis ─────────────────────────────────────
    update("synthesizing")
    enriched_clusters, digest = synthesize(
        clusters, total_reviews=len(clean_reviews),
        sources=sources, progress_callback=update
    )
    update("synthesis_done")

    # ── Save outputs ──────────────────────────────────────────────────
    completed_at = datetime.now().isoformat()
    out_dir = f"{OUTPUTS_DIR}/{run_id}"
    os.makedirs(out_dir, exist_ok=True)

    with open(f"{out_dir}/filter_log.json", "w") as f:
        json.dump(filter_log, f, indent=2)
    with open(f"{out_dir}/enriched_reviews.json", "w") as f:
        json.dump(enriched, f, indent=2)
    with open(f"{out_dir}/opportunity_clusters.json", "w") as f:
        json.dump(enriched_clusters, f, indent=2)
    with open(f"{out_dir}/digest.md", "w") as f:
        f.write(digest)

    save_run(
        run_id=run_id, started_at=started_at, completed_at=completed_at,
        sources=sources, days=days,
        total_raw=len(all_raw),
        total_filtered=filter_log["total_raw"] - filter_log["passed"],
        total_clean=filter_log["passed"],
        filter_log=filter_log, status="completed",
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
        "clusters": enriched_clusters,
        "digest": digest,
    }

    update(f"done:{run_id}")
    return result
