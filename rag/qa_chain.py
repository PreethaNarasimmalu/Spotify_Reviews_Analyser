import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.embedder import retrieve
from pipeline.extractor import get_pool

QA_PROMPT = """You are a product researcher at Spotify analyzing user feedback to find product opportunities.

A product manager has asked: "{question}"

Here are the {count} most relevant user reviews retrieved from our feedback database:

{reviews}

Based ONLY on these reviews, answer the question with:
1. A clear, evidence-based answer (2-3 sentences)
2. The key patterns you see (bullet points, max 4)
3. Signal strength: what % of these reviews relate directly to the question

Be specific and grounded — quote exact phrases where useful.
If the reviews don't have enough signal to answer confidently, say so.

Return a JSON object with:
- "answer": your main answer paragraph
- "key_patterns": list of pattern strings (max 4)
- "signal_strength_pct": integer 0-100
- "supporting_quotes": list of up to 4 objects with "quote", "source", "date", "rating"
- "opportunity_hypothesis": one sentence product opportunity framing

Only valid JSON, no explanation.
"""

PREDEFINED_QUESTIONS = [
    "Why do users struggle to discover new music?",
    "What are the most common frustrations with recommendations?",
    "What listening behaviors are users trying to achieve?",
    "What causes users to repeatedly listen to the same content?",
    "Which user segments experience different discovery challenges?",
    "What unmet needs emerge consistently across reviews?",
]


def ask(question: str, top_k: int = 15) -> dict:
    hits = retrieve(question, top_k=top_k)

    if not hits:
        return {
            "answer": "No reviews indexed yet. Please run an analysis first.",
            "key_patterns": [],
            "signal_strength_pct": 0,
            "supporting_quotes": [],
            "opportunity_hypothesis": "",
        }

    reviews_text = "\n\n".join(
        f"[{i+1}] ({h['source']} · {h['date']} · "
        f"{'★' * int(h['rating']) if h['rating'].isdigit() else 'no rating'}) "
        f"{h['text'][:300]}"
        for i, h in enumerate(hits)
    )

    prompt = QA_PROMPT.format(
        question=question,
        count=len(hits),
        reviews=reviews_text,
    )

    raw = get_pool().call(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=800,
    )

    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
    except Exception:
        result = {
            "answer": raw,
            "key_patterns": [],
            "signal_strength_pct": 0,
            "supporting_quotes": [],
            "opportunity_hypothesis": "",
        }

    result["retrieved_count"] = len(hits)
    result["question"] = question
    return result
