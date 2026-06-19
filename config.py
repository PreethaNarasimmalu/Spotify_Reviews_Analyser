from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SpotifyReviewAnalyser/1.0")

SPOTIFY_APP_ID_IOS = "324684580"
SPOTIFY_PACKAGE_ANDROID = "com.spotify.music"

REDDIT_SUBREDDITS = ["spotify", "musicrecommendations", "spotifyplaylist"]
REDDIT_SEARCH_TERMS = [
    "discover weekly", "recommendation", "same songs", "music discovery",
    "algorithm", "new music", "playlist", "repeat"
]

DB_PATH = "data/reviews.db"
OUTPUTS_DIR = "outputs"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

MIN_WORD_COUNT = 3
MAX_JUNK_RATIO = 0.30
DUPLICATE_SIMILARITY_THRESHOLD = 0.80
