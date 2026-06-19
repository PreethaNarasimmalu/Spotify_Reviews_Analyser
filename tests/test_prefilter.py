import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.prefilter import (
    normalize_repeated_chars,
    junk_ratio,
    is_mostly_emoji,
    has_min_words,
    is_near_duplicate,
    filter_reviews,
)


def test_normalize_repeated_chars():
    assert normalize_repeated_chars("plssssss fix this") == "plss fix this"
    assert normalize_repeated_chars("heyyyy") == "heyy"
    assert normalize_repeated_chars("hello") == "hello"


def test_junk_ratio():
    assert junk_ratio("hello world") < 0.30
    assert junk_ratio("🔥🔥🔥🔥🔥") > 0.30
    assert junk_ratio("!!!###$$$%%%") > 0.30


def test_is_mostly_emoji():
    assert is_mostly_emoji("😍😍😍💚💚") == True
    assert is_mostly_emoji("great app 😍") == False
    assert is_mostly_emoji("same songs every time") == False


def test_has_min_words():
    assert has_min_words("same songs always") == True       # 3 words — keep
    assert has_min_words("love it") == False                # 2 words — drop
    assert has_min_words("nice") == False                   # 1 word — drop
    assert has_min_words("") == False
    assert has_min_words("discover weekly is broken") == True



def test_is_near_duplicate():
    seen = ["The app keeps playing the same songs over and over again"]
    assert is_near_duplicate("The app keeps playing the same songs over and over again", seen) == True
    assert is_near_duplicate("Discover Weekly never shows new artists", seen) == False


def test_filter_reviews_full():
    raw = [
        {"text": "", "source": "app_store", "platform": "ios", "rating": 2, "date": "", "user_id": ""},
        {"text": "nice", "source": "app_store", "platform": "ios", "rating": 5, "date": "", "user_id": ""},
        {"text": "love it", "source": "app_store", "platform": "ios", "rating": 5, "date": "", "user_id": ""},
        {"text": "😍😍😍😍😍😍", "source": "play_store", "platform": "android", "rating": 5, "date": "", "user_id": ""},
        {"text": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥", "source": "play_store", "platform": "android", "rating": 5, "date": "", "user_id": ""},
        {"text": "same songs always", "source": "app_store", "platform": "ios", "rating": 2, "date": "", "user_id": ""},
        {"text": "same songs always", "source": "app_store", "platform": "ios", "rating": 2, "date": "", "user_id": ""},
        {"text": "Discover Weekly never shows me new artists, it just recycles the same ones I already know", "source": "reddit", "platform": "reddit", "rating": None, "date": "", "user_id": ""},
        {"text": "The algorithm thinks I only like sad indie music because I listened to it once", "source": "app_store", "platform": "ios", "rating": 2, "date": "", "user_id": ""},
    ]

    clean, log = filter_reviews(raw)

    print("\n=== Filter Results ===")
    print(f"Total raw:        {log['total_raw']}")
    print(f"Dropped no text:  {log['dropped_no_text']}")
    print(f"Dropped min words:{log['dropped_min_words']}")
    print(f"Dropped emoji:    {log['dropped_emoji_only']}")
    print(f"Dropped junk:     {log['dropped_junk_chars']}")
    print(f"Dropped duplicate:{log['dropped_duplicate']}")
    print(f"Passed:           {log['passed']}")
    print("\nClean reviews:")
    for r in clean:
        print(f"  → {r['text'][:80]}")

    assert log["dropped_no_text"] == 1       # empty text
    assert log["dropped_min_words"] == 2     # "nice" and "love it"
    assert log["dropped_emoji_only"] >= 1    # emoji-only reviews
    assert log["dropped_duplicate"] == 1     # second "same songs always"
    assert log["passed"] >= 3               # "same songs always", and 2 long reviews
    assert any("same songs always" in r["text"] for r in clean)
    assert any("Discover Weekly" in r["text"] for r in clean)


if __name__ == "__main__":
    test_normalize_repeated_chars()
    test_junk_ratio()
    test_is_mostly_emoji()
    test_has_min_words()
    test_is_near_duplicate()
    test_filter_reviews_full()
    print("\n✅ All tests passed")
