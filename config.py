from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SPOTIFY_APP_ID_IOS = "324684580"
SPOTIFY_PACKAGE_ANDROID = "com.spotify.music"

DB_PATH = "data/reviews.db"
OUTPUTS_DIR = "outputs"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

MIN_WORD_COUNT = 3
MAX_JUNK_RATIO = 0.30
DUPLICATE_SIMILARITY_THRESHOLD = 0.80
