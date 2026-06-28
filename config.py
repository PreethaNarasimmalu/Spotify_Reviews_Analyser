from dotenv import load_dotenv
import os

load_dotenv()

# Groq API keys — rotated automatically on failure
GROQ_API_KEYS = [
    k for k in [
        os.getenv("GROQ_API_KEY_1"),
        os.getenv("GROQ_API_KEY_2"),
        os.getenv("GROQ_API_KEY_3"),
        os.getenv("GROQ_API_KEY_4"),
        os.getenv("GROQ_API_KEY_5"),
    ] if k
]
# Fallback: support single key for backward compatibility
if not GROQ_API_KEYS and os.getenv("GROQ_API_KEY"):
    GROQ_API_KEYS = [os.getenv("GROQ_API_KEY")]

SPOTIFY_APP_ID_IOS = "324684580"
SPOTIFY_PACKAGE_ANDROID = "com.spotify.music"

DB_PATH = "data/reviews.db"
OUTPUTS_DIR = "outputs"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

MIN_WORD_COUNT = 3
MAX_JUNK_RATIO = 0.30
DUPLICATE_SIMILARITY_THRESHOLD = 0.80

GROQ_BATCH_SIZE = 50        # reviews per Groq call (up from 20)
TOP_CLUSTERS_FOR_SYNTHESIS = 4  # Claude only synthesizes top 4 clusters
