from dotenv import load_dotenv
import os

load_dotenv()


def _get_secret(key: str) -> str | None:
    """Read from Streamlit secrets (cloud) or env vars (local)."""
    try:
        import streamlit as st
        return st.secrets.get(key)
    except Exception:
        return os.getenv(key)


# Groq API keys — rotated automatically on failure
GROQ_API_KEYS = [
    k for k in [
        _get_secret("GROQ_API_KEY_1"),
        _get_secret("GROQ_API_KEY_2"),
        _get_secret("GROQ_API_KEY_3"),
        _get_secret("GROQ_API_KEY_4"),
        _get_secret("GROQ_API_KEY_5"),
    ] if k
]
# Fallback: single key
if not GROQ_API_KEYS and _get_secret("GROQ_API_KEY"):
    GROQ_API_KEYS = [_get_secret("GROQ_API_KEY")]

SPOTIFY_APP_ID_IOS = "324684580"
SPOTIFY_PACKAGE_ANDROID = "com.spotify.music"

DB_PATH = "data/reviews.db"
OUTPUTS_DIR = "outputs"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

MIN_WORD_COUNT = 3
MAX_JUNK_RATIO = 0.30
DUPLICATE_SIMILARITY_THRESHOLD = 0.80

GROQ_BATCH_SIZE = 50
TOP_CLUSTERS_FOR_SYNTHESIS = 4
