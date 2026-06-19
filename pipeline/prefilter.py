import re
import unicodedata
from difflib import SequenceMatcher
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MIN_WORD_COUNT, MAX_JUNK_RATIO, DUPLICATE_SIMILARITY_THRESHOLD


def normalize_repeated_chars(text: str) -> str:
    return re.sub(r'(.)\1{2,}', r'\1\1', text)


def junk_ratio(text: str) -> float:
    if not text:
        return 1.0
    alpha = sum(1 for c in text if c.isalpha() or c.isspace())
    return 1 - (alpha / len(text))


def is_mostly_emoji(text: str) -> bool:
    emoji_count = sum(1 for c in text if unicodedata.category(c) in ("So", "Sm"))
    return len(text) > 0 and emoji_count / len(text) > 0.5


def has_min_words(text: str) -> bool:
    words = [w for w in text.split() if w.isalpha()]
    return len(words) >= MIN_WORD_COUNT



def is_near_duplicate(text: str, seen: list[str]) -> bool:
    for s in seen:
        ratio = SequenceMatcher(None, text.lower(), s.lower()).ratio()
        if ratio >= DUPLICATE_SIMILARITY_THRESHOLD:
            return True
    return False


def filter_reviews(raw_reviews: list[dict]) -> tuple[list[dict], dict]:
    clean = []
    seen_texts = []
    log = {
        "total_raw": len(raw_reviews),
        "dropped_no_text": 0,
        "dropped_min_words": 0,
        "dropped_emoji_only": 0,
        "dropped_junk_chars": 0,
        "dropped_duplicate": 0,
        "passed": 0,
    }

    for review in raw_reviews:
        text = (review.get("text") or "").strip()

        if not text:
            log["dropped_no_text"] += 1
            continue

        text = normalize_repeated_chars(text)

        if is_mostly_emoji(text):
            log["dropped_emoji_only"] += 1
            continue

        if junk_ratio(text) > MAX_JUNK_RATIO:
            log["dropped_junk_chars"] += 1
            continue

        if not has_min_words(text):
            log["dropped_min_words"] += 1
            continue

        if is_near_duplicate(text, seen_texts):
            log["dropped_duplicate"] += 1
            continue

        seen_texts.append(text)
        review["text"] = text
        clean.append(review)
        log["passed"] += 1

    return clean, log
