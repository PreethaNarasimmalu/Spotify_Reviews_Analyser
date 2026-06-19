import sqlite3
import json
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            platform TEXT,
            text TEXT,
            rating REAL,
            date TEXT,
            user_id TEXT,
            title TEXT,
            run_id TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT,
            completed_at TEXT,
            sources TEXT,
            days INTEGER,
            total_raw INTEGER,
            total_filtered INTEGER,
            total_clean INTEGER,
            filter_log TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_reviews(reviews: list[dict], run_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for r in reviews:
        c.execute("""
            INSERT INTO reviews (source, platform, text, rating, date, user_id, title, run_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r.get("source"), r.get("platform"), r.get("text"),
            r.get("rating"), r.get("date"), r.get("user_id"),
            r.get("title", ""), run_id, datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()


def save_run(run_id: str, started_at: str, completed_at: str, sources: list,
             days: int, total_raw: int, total_filtered: int, total_clean: int,
             filter_log: dict, status: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO runs
        (run_id, started_at, completed_at, sources, days, total_raw, total_filtered, total_clean, filter_log, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id, started_at, completed_at, json.dumps(sources),
        days, total_raw, total_filtered, total_clean,
        json.dumps(filter_log), status
    ))
    conn.commit()
    conn.close()


def get_last_run() -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM runs WHERE status = 'completed' ORDER BY completed_at DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["sources"] = json.loads(d["sources"])
    d["filter_log"] = json.loads(d["filter_log"])
    return d


def get_reviews_by_run(run_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM reviews WHERE run_id = ?", (run_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
