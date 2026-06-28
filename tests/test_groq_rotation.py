import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock
from pipeline.extractor import GroqClientPool


def _mock_pool(num_keys: int) -> GroqClientPool:
    pool = GroqClientPool.__new__(GroqClientPool)
    pool.keys = [f"key{i}" for i in range(num_keys)]
    pool.index = 0
    pool.clients = [MagicMock() for _ in range(num_keys)]
    return pool


def test_key_rotation():
    """key1 fails, key2 fails, key3 succeeds — should rotate and return result."""
    pool = _mock_pool(3)

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "[]"

    pool.clients[0].chat.completions.create.side_effect = Exception("rate limit")
    pool.clients[1].chat.completions.create.side_effect = Exception("rate limit")
    pool.clients[2].chat.completions.create.return_value = mock_response

    result = pool.call(model="x", messages=[], temperature=0, max_tokens=10)

    assert result == "[]"
    assert pool.index == 2
    print("  ✅ Rotated key1 → key2 → key3 on failures, succeeded on key3")


def test_all_keys_fail():
    """All keys fail — should raise RuntimeError."""
    pool = _mock_pool(2)
    for c in pool.clients:
        c.chat.completions.create.side_effect = Exception("fail")

    try:
        pool.call(model="x", messages=[], temperature=0, max_tokens=10)
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        print(f"  ✅ RuntimeError raised when all keys fail: {e}")


def test_no_rotation_on_success():
    """First key succeeds — should not rotate."""
    pool = _mock_pool(3)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "success"
    pool.clients[0].chat.completions.create.return_value = mock_response

    result = pool.call(model="x", messages=[], temperature=0, max_tokens=10)
    assert result == "success"
    assert pool.index == 0
    print("  ✅ No rotation when first key succeeds")


def test_batch_size_config():
    from config import GROQ_BATCH_SIZE
    assert GROQ_BATCH_SIZE == 50
    print(f"  ✅ GROQ_BATCH_SIZE = {GROQ_BATCH_SIZE}")


def test_top_clusters_config():
    from config import TOP_CLUSTERS_FOR_SYNTHESIS
    assert TOP_CLUSTERS_FOR_SYNTHESIS == 4
    print(f"  ✅ TOP_CLUSTERS_FOR_SYNTHESIS = {TOP_CLUSTERS_FOR_SYNTHESIS}")


if __name__ == "__main__":
    test_key_rotation()
    test_all_keys_fail()
    test_no_rotation_on_success()
    test_batch_size_config()
    test_top_clusters_config()
    print("\n✅ All Groq rotation tests passed")
