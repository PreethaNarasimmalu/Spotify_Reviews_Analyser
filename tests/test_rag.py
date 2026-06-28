import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
import rag.embedder as embedder_module

MOCK_REVIEWS = [
    {
        "text": "Discover Weekly keeps giving me artists I already follow. No new music at all.",
        "source": "app_store", "platform": "ios", "rating": "2",
        "date": "2026-06-10", "run_id": "test_run",
        "analysis": {"topics": ["discovery"], "sentiment": "negative", "user_segment": "power_user"},
    },
    {
        "text": "The algorithm trapped me in the same genre bubble for two years.",
        "source": "play_store", "platform": "android", "rating": "2",
        "date": "2026-06-12", "run_id": "test_run",
        "analysis": {"topics": ["repeat_listening"], "sentiment": "negative", "user_segment": "audiophile"},
    },
    {
        "text": "I want a way to tell Spotify I am in the mood for something completely new.",
        "source": "community", "platform": "community", "rating": "",
        "date": "2026-06-15", "run_id": "test_run",
        "analysis": {"topics": ["ux", "discovery"], "sentiment": "mixed", "user_segment": "casual"},
    },
    {
        "text": "Great sound quality and the offline mode works perfectly.",
        "source": "app_store", "platform": "ios", "rating": "5",
        "date": "2026-06-18", "run_id": "test_run",
        "analysis": {"topics": ["other"], "sentiment": "positive", "user_segment": "casual"},
    },
    {
        "text": "Same songs on daily mix for six months. Nothing ever changes.",
        "source": "play_store", "platform": "android", "rating": "1",
        "date": "2026-06-17", "run_id": "test_run",
        "analysis": {"topics": ["repeat_listening"], "sentiment": "negative", "user_segment": "power_user"},
    },
]


def _mock_collection():
    col = MagicMock()
    col.count.return_value = len(MOCK_REVIEWS)
    return col


def test_index_reviews_calls_collection_add():
    """index_reviews prepares correct docs, metadatas, ids and calls add."""
    col = _mock_collection()
    with patch.object(embedder_module, "_get_collection", return_value=col):
        count = embedder_module.index_reviews(MOCK_REVIEWS, run_id="test_run")

    assert col.add.called
    args = col.add.call_args_list[0][1]
    assert len(args["documents"]) == len(MOCK_REVIEWS)
    assert len(args["metadatas"]) == len(MOCK_REVIEWS)
    assert len(args["ids"]) == len(MOCK_REVIEWS)
    assert count == len(MOCK_REVIEWS)
    print(f"  ✅ index_reviews indexed {count} reviews correctly")


def test_index_reviews_skips_empty_text():
    """Reviews with empty text must be skipped."""
    reviews_with_empty = MOCK_REVIEWS + [
        {"text": "", "source": "app_store", "platform": "ios", "rating": "3",
         "date": "2026-06-01", "run_id": "test_run", "analysis": {}}
    ]
    col = _mock_collection()
    with patch.object(embedder_module, "_get_collection", return_value=col):
        count = embedder_module.index_reviews(reviews_with_empty, run_id="test_run")

    assert count == len(MOCK_REVIEWS)
    print(f"  ✅ Empty text skipped — indexed {count} of {len(reviews_with_empty)}")


def test_retrieve_returns_hits():
    """retrieve() correctly maps ChromaDB results into hit dicts."""
    col = _mock_collection()
    col.query.return_value = {
        "documents": [["Same songs on daily mix.", "Trapped in genre bubble."]],
        "metadatas": [[
            {"source": "play_store", "date": "2026-06-17", "rating": "1",
             "sentiment": "negative", "user_segment": "power_user"},
            {"source": "play_store", "date": "2026-06-12", "rating": "2",
             "sentiment": "negative", "user_segment": "audiophile"},
        ]],
        "distances": [[0.1, 0.25]],
    }

    with patch.object(embedder_module, "_get_collection", return_value=col):
        hits = embedder_module.retrieve("why do users hear the same songs", top_k=2)

    assert len(hits) == 2
    assert hits[0]["relevance_score"] == round(1 - 0.1, 3)
    assert hits[0]["source"] == "play_store"
    assert "text" in hits[0]
    print(f"  ✅ retrieve() returned {len(hits)} hits")
    for h in hits:
        print(f"      [{h['relevance_score']}] {h['text']}")


def test_metadata_fields_stored():
    """All required metadata fields must be present per review."""
    col = _mock_collection()
    with patch.object(embedder_module, "_get_collection", return_value=col):
        embedder_module.index_reviews(MOCK_REVIEWS[:1], run_id="test_run")

    meta = col.add.call_args[1]["metadatas"][0]
    required = {"source", "platform", "rating", "date", "run_id", "topics", "sentiment", "user_segment"}
    missing = required - set(meta.keys())
    assert not missing, f"Missing metadata fields: {missing}"
    print(f"  ✅ All metadata fields stored: {sorted(meta.keys())}")


def test_ids_are_unique():
    """Each indexed review must have a unique ID."""
    col = _mock_collection()
    with patch.object(embedder_module, "_get_collection", return_value=col):
        embedder_module.index_reviews(MOCK_REVIEWS, run_id="test_run")

    ids = col.add.call_args[1]["ids"]
    assert len(ids) == len(set(ids)), "IDs must be unique"
    print(f"  ✅ All {len(ids)} IDs are unique")


if __name__ == "__main__":
    test_index_reviews_calls_collection_add()
    test_index_reviews_skips_empty_text()
    test_retrieve_returns_hits()
    test_metadata_fields_stored()
    test_ids_are_unique()
    print("\n✅ All RAG tests passed")
