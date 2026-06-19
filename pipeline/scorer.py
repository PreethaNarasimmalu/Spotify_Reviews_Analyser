from collections import defaultdict
from datetime import datetime, timedelta


TOPIC_LABELS = {
    "discovery": "Music Discovery Friction",
    "recommendation": "Recommendation Mismatch",
    "repeat_listening": "Echo Chamber / Repeat Loop",
    "algorithm": "Algorithm Behavior",
    "ux": "Discovery Surface UX",
    "playlist": "Playlist & Radio Issues",
    "social": "Social Discovery Gap",
    "other": "Other",
}


def score_opportunities(enriched_reviews: list[dict]) -> list[dict]:
    now = datetime.now()
    topic_data = defaultdict(lambda: {
        "reviews": [],
        "frustrations": [],
        "key_quotes": [],
        "segments": defaultdict(int),
        "sentiments": defaultdict(int),
        "recent_count": 0,
    })

    for r in enriched_reviews:
        analysis = r.get("analysis", {})
        if not analysis.get("discovery_related"):
            continue

        topics = analysis.get("topics", []) or ["other"]
        for topic in topics:
            td = topic_data[topic]
            td["reviews"].append(r)

            for f in (analysis.get("frustration_signals") or []):
                td["frustrations"].append(f)

            quote = analysis.get("key_quote")
            if quote:
                td["key_quotes"].append({
                    "quote": quote,
                    "source": r.get("source", ""),
                    "date": r.get("date", ""),
                    "rating": r.get("rating"),
                })

            seg = analysis.get("user_segment", "unknown")
            td["segments"][seg] += 1

            sent = analysis.get("sentiment", "neutral")
            td["sentiments"][sent] += 1

            try:
                date = datetime.fromisoformat(r.get("date", ""))
                if date >= now - timedelta(days=30):
                    td["recent_count"] += 1
            except Exception:
                pass

    clusters = []
    total_discovery = sum(len(td["reviews"]) for td in topic_data.values()) or 1

    for topic, td in topic_data.items():
        count = len(td["reviews"])
        if count == 0:
            continue

        frequency = count / total_discovery
        negative = td["sentiments"].get("negative", 0) + td["sentiments"].get("mixed", 0)
        intensity = negative / count if count else 0
        recency = td["recent_count"] / count if count else 0

        signal_strength = round((frequency * 0.4 + intensity * 0.4 + recency * 0.2) * 100)

        top_frustrations = _top_n(td["frustrations"], 5)
        top_segment = max(td["segments"], key=td["segments"].get) if td["segments"] else "unknown"

        clusters.append({
            "topic": topic,
            "label": TOPIC_LABELS.get(topic, topic),
            "count": count,
            "signal_strength": signal_strength,
            "frequency_pct": round(frequency * 100, 1),
            "intensity_pct": round(intensity * 100, 1),
            "recency_pct": round(recency * 100, 1),
            "top_frustrations": top_frustrations,
            "top_segment": top_segment,
            "segment_breakdown": dict(td["segments"]),
            "sentiment_breakdown": dict(td["sentiments"]),
            "key_quotes": td["key_quotes"][:5],
        })

    clusters.sort(key=lambda x: x["signal_strength"], reverse=True)
    return clusters


def _top_n(items: list[str], n: int) -> list[str]:
    freq = defaultdict(int)
    for item in items:
        freq[item.lower().strip()] += 1
    return [k for k, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]]
