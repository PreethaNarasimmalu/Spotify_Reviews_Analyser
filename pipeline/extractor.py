import json
from groq import Groq
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEYS, GROQ_BATCH_SIZE


class GroqClientPool:
    """Rotates through multiple Groq API keys on rate limit or error."""

    def __init__(self, api_keys: list[str]):
        if not api_keys:
            raise ValueError("No Groq API keys configured. Add GROQ_API_KEY_1 ... GROQ_API_KEY_5 to .env")
        self.keys = api_keys
        self.index = 0
        self.clients = [Groq(api_key=k) for k in api_keys]

    @property
    def current(self) -> Groq:
        return self.clients[self.index]

    def rotate(self):
        self.index = (self.index + 1) % len(self.clients)
        print(f"[Groq] Rotated to key #{self.index + 1}")

    def call(self, **kwargs) -> str:
        last_error = None
        for _ in range(len(self.clients)):
            try:
                response = self.current.chat.completions.create(**kwargs)
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Groq] Key #{self.index + 1} failed: {e}")
                last_error = e
                self.rotate()
        raise RuntimeError(f"All Groq API keys failed. Last error: {last_error}")


_pool = None

def get_pool() -> GroqClientPool:
    global _pool
    if _pool is None:
        _pool = GroqClientPool(GROQ_API_KEYS)
    return _pool


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
        f"[{i}] {r['text'][:400]}" for i, r in enumerate(reviews)
    )

    raw = get_pool().call(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(reviews=numbered)}],
        temperature=0.1,
        max_tokens=6000,
    )

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


def extract_all(reviews: list[dict], batch_size: int = GROQ_BATCH_SIZE,
                progress_callback=None) -> list[dict]:
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
