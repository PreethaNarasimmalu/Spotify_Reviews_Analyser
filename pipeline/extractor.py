import json
from groq import Groq
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

EXTRACTION_PROMPT = """You are analyzing Spotify user reviews to identify music discovery problems and opportunities.

For each review below, extract structured information in JSON format.

Reviews:
{reviews}

For EACH review return a JSON object with these fields:
- "index": the review number (0-based)
- "topics": list of topics from: ["discovery", "recommendation", "repeat_listening", "algorithm", "ux", "playlist", "social", "other"]
- "frustration_signals": list of specific frustrations mentioned (short phrases, empty list if none)
- "behavior_intent": what the user was trying to do (one short sentence, null if unclear)
- "user_segment": one of ["casual", "power_user", "audiophile", "unknown"]
- "sentiment": one of ["positive", "negative", "neutral", "mixed"]
- "discovery_related": true if this review is about music discovery or recommendations, false otherwise
- "key_quote": the most insightful 1-2 sentence excerpt from this review (verbatim), null if nothing stands out

Return a JSON array of objects, one per review. No explanation, only valid JSON.
"""


def extract_batch(reviews: list[dict]) -> list[dict]:
    numbered = "\n\n".join(
        f"[{i}] {r['text'][:500]}" for i, r in enumerate(reviews)
    )

    prompt = EXTRACTION_PROMPT.format(reviews=numbered)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()

    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"[Groq] Parse error: {e}\nRaw: {raw[:300]}")
        return [{"index": i, "topics": [], "frustration_signals": [], "behavior_intent": None,
                 "user_segment": "unknown", "sentiment": "neutral", "discovery_related": False,
                 "key_quote": None} for i in range(len(reviews))]


def extract_all(reviews: list[dict], batch_size: int = 20, progress_callback=None) -> list[dict]:
    enriched = []
    total_batches = (len(reviews) + batch_size - 1) // batch_size

    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i + batch_size]
        batch_num = i // batch_size + 1

        if progress_callback:
            progress_callback(f"groq_batch:{batch_num}/{total_batches}")

        results = extract_batch(batch)

        for j, review in enumerate(batch):
            meta = next((r for r in results if r.get("index") == j), {})
            enriched.append({**review, "analysis": meta})

    return enriched
