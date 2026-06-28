import anthropic
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, TOP_CLUSTERS_FOR_SYNTHESIS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

HYPOTHESIS_PROMPT = """You are a product strategist analyzing Spotify user feedback.

Based on this opportunity cluster from user reviews, write a concise hypothesis card.

Cluster: {label}
Signal Strength: {signal_strength}/100
Review Count: {count}
Top Frustrations: {frustrations}
Top User Segment: {segment}
Sample Quotes:
{quotes}

Return a JSON object with:
- "hypothesis": one paragraph (3-4 sentences) describing the core user problem, who experiences it, and why it matters for Spotify
- "opportunity": one sentence framing the product opportunity
- "validation_questions": list of 2-3 questions to ask users in interviews to validate this

Only valid JSON, no explanation.
"""

DIGEST_PROMPT = """You are a senior product researcher at Spotify summarizing weekly user feedback analysis.

Here are the top opportunity clusters found from analyzing {total_reviews} user reviews across {sources}:

{clusters_summary}

Write a concise executive digest (4-6 sentences) that:
1. Names the single biggest opportunity and why it stands out
2. Identifies which user segment is most affected
3. Notes any surprising or counterintuitive findings
4. Ends with a recommended next step for the product team

Plain text, no headers, no bullet points.
"""


def generate_hypothesis(cluster: dict) -> dict:
    quotes_text = "\n".join(
        f'- "{q["quote"]}" ({q["source"]}, {q["date"][:10] if q["date"] else "unknown"})'
        for q in cluster.get("key_quotes", [])[:3]
    ) or "No quotes available"

    prompt = HYPOTHESIS_PROMPT.format(
        label=cluster["label"],
        signal_strength=cluster["signal_strength"],
        count=cluster["count"],
        frustrations=", ".join(cluster.get("top_frustrations", [])) or "none listed",
        segment=cluster.get("top_segment", "unknown"),
        quotes=quotes_text,
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return {"hypothesis": raw, "opportunity": "", "validation_questions": []}


def generate_digest(clusters: list[dict], total_reviews: int, sources: list[str]) -> str:
    clusters_summary = "\n".join(
        f"{i+1}. {c['label']} — Signal {c['signal_strength']}/100, {c['count']} reviews, "
        f"top segment: {c.get('top_segment', 'unknown')}, "
        f"top frustrations: {', '.join(c.get('top_frustrations', [])[:3])}"
        for i, c in enumerate(clusters[:6])
    )

    prompt = DIGEST_PROMPT.format(
        total_reviews=total_reviews,
        sources=", ".join(sources),
        clusters_summary=clusters_summary,
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text.strip()


def synthesize(clusters: list[dict], total_reviews: int, sources: list[str],
               progress_callback=None) -> tuple[list[dict], str]:
    enriched_clusters = []
    top_clusters = clusters[:TOP_CLUSTERS_FOR_SYNTHESIS]

    for i, cluster in enumerate(top_clusters):
        if progress_callback:
            progress_callback(f"claude_hypothesis:{i+1}/{len(top_clusters)}")
        hypothesis = generate_hypothesis(cluster)
        enriched_clusters.append({**cluster, "hypothesis": hypothesis})

    # Append remaining clusters without hypothesis (still shown in dashboard)
    for cluster in clusters[TOP_CLUSTERS_FOR_SYNTHESIS:]:
        enriched_clusters.append({**cluster, "hypothesis": None})

    if progress_callback:
        progress_callback("claude_digest")
    digest = generate_digest(enriched_clusters, total_reviews, sources)

    return enriched_clusters, digest
