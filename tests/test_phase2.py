import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.scorer import score_opportunities

MOCK_ENRICHED = [
    {
        "source": "app_store", "platform": "ios", "rating": 2,
        "date": "2026-06-10T10:00:00", "user_id": "u1",
        "text": "Discover Weekly keeps giving me artists I already follow. No new music at all.",
        "analysis": {
            "topics": ["discovery", "recommendation"],
            "frustration_signals": ["discover weekly not new", "same artists"],
            "behavior_intent": "find new music",
            "user_segment": "power_user",
            "sentiment": "negative",
            "discovery_related": True,
            "key_quote": "Discover Weekly keeps giving me artists I already follow.",
        }
    },
    {
        "source": "play_store", "platform": "android", "rating": 2,
        "date": "2026-06-12T10:00:00", "user_id": "u2",
        "text": "The algorithm trapped me in the same genre bubble for 2 years.",
        "analysis": {
            "topics": ["repeat_listening", "algorithm"],
            "frustration_signals": ["genre bubble", "algorithm stuck"],
            "behavior_intent": "explore different genres",
            "user_segment": "audiophile",
            "sentiment": "negative",
            "discovery_related": True,
            "key_quote": "The algorithm trapped me in the same genre bubble for 2 years.",
        }
    },
    {
        "source": "reddit", "platform": "reddit", "rating": None,
        "date": "2026-06-15T10:00:00", "user_id": "u3",
        "text": "I just want a way to tell Spotify I am in the mood for something completely new.",
        "analysis": {
            "topics": ["ux", "discovery"],
            "frustration_signals": ["no mood controls", "no exploration mode"],
            "behavior_intent": "discover new music intentionally",
            "user_segment": "casual",
            "sentiment": "mixed",
            "discovery_related": True,
            "key_quote": "I just want a way to tell Spotify I am in the mood for something completely new.",
        }
    },
    {
        "source": "app_store", "platform": "ios", "rating": 5,
        "date": "2026-06-18T10:00:00", "user_id": "u4",
        "text": "Great app, love the sound quality and offline mode.",
        "analysis": {
            "topics": ["other"],
            "frustration_signals": [],
            "behavior_intent": "listen to music offline",
            "user_segment": "casual",
            "sentiment": "positive",
            "discovery_related": False,
            "key_quote": None,
        }
    },
    {
        "source": "reddit", "platform": "reddit", "rating": None,
        "date": "2026-06-17T10:00:00", "user_id": "u5",
        "text": "Same songs every single time on my daily mix. Six months and nothing changes.",
        "analysis": {
            "topics": ["repeat_listening", "recommendation"],
            "frustration_signals": ["daily mix repetitive", "no variety"],
            "behavior_intent": "get varied music recommendations",
            "user_segment": "power_user",
            "sentiment": "negative",
            "discovery_related": True,
            "key_quote": "Same songs every single time on my daily mix.",
        }
    },
]


def test_scorer_produces_clusters():
    clusters = score_opportunities(MOCK_ENRICHED)
    print("\n=== Opportunity Clusters ===")
    for c in clusters:
        print(f"  {c['label']:<35} signal={c['signal_strength']:>3}  count={c['count']}  segment={c['top_segment']}")
        print(f"    frustrations: {c['top_frustrations']}")

    assert len(clusters) > 0, "Should produce at least one cluster"
    assert all("signal_strength" in c for c in clusters), "All clusters need signal_strength"
    assert clusters == sorted(clusters, key=lambda x: x["signal_strength"], reverse=True), \
        "Clusters should be sorted by signal_strength descending"
    print(f"\n  Top opportunity: {clusters[0]['label']} (signal={clusters[0]['signal_strength']})")


def test_scorer_excludes_non_discovery():
    clusters = score_opportunities(MOCK_ENRICHED)
    # non-discovery review (u4, "other" topic) should not appear in any cluster quote
    for c in clusters:
        for q in c.get("key_quotes", []):
            assert "offline" not in q.get("quote", "").lower(), \
                "Non-discovery review should be excluded from clusters"


def test_scorer_key_quotes():
    clusters = score_opportunities(MOCK_ENRICHED)
    quotes_found = any(c.get("key_quotes") for c in clusters)
    assert quotes_found, "Should have at least some key quotes"


def test_scorer_segment_breakdown():
    clusters = score_opportunities(MOCK_ENRICHED)
    for c in clusters:
        assert "segment_breakdown" in c
        assert isinstance(c["segment_breakdown"], dict)


if __name__ == "__main__":
    test_scorer_produces_clusters()
    test_scorer_excludes_non_discovery()
    test_scorer_key_quotes()
    test_scorer_segment_breakdown()
    print("\n✅ All Phase 2 scorer tests passed")
