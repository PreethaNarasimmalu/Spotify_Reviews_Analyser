SPOTIFY_CSS = """
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #191414;
    color: #FFFFFF;
}
[data-testid="stSidebar"] {
    background-color: #121212;
    border-right: 1px solid #282828;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* ── Headers ── */
h1, h2, h3, h4 { color: #FFFFFF !important; }
h1 span.green { color: #1DB954; }

/* ── Buttons ── */
.stButton > button {
    background-color: #1DB954;
    color: #000000;
    font-weight: 700;
    border: none;
    border-radius: 500px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: #1ed760;
    transform: scale(1.03);
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background-color: #282828;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #3E3E3E;
}
[data-testid="metric-container"] label { color: #B3B3B3 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1DB954 !important;
    font-size: 2rem !important;
}

/* ── Cards ── */
.spotify-card {
    background-color: #282828;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #3E3E3E;
}
.spotify-card:hover { border-color: #1DB954; }

/* ── Quote cards ── */
.quote-card {
    background-color: #1a1a1a;
    border-left: 3px solid #1DB954;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-style: italic;
    color: #E0E0E0;
}
.quote-meta {
    font-size: 0.78rem;
    color: #B3B3B3;
    margin-top: 0.3rem;
    font-style: normal;
}

/* ── Signal badges ── */
.badge-high   { background:#1DB954; color:#000; padding:2px 10px; border-radius:500px; font-weight:700; font-size:0.8rem; }
.badge-medium { background:#F59B23; color:#000; padding:2px 10px; border-radius:500px; font-weight:700; font-size:0.8rem; }
.badge-low    { background:#535353; color:#fff; padding:2px 10px; border-radius:500px; font-weight:700; font-size:0.8rem; }

/* ── Progress ── */
.stProgress > div > div { background-color: #1DB954 !important; }

/* ── Tabs ── */
[data-testid="stTab"] { color: #B3B3B3 !important; }
[data-testid="stTab"][aria-selected="true"] {
    color: #1DB954 !important;
    border-bottom: 2px solid #1DB954 !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stMultiSelect"] {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    border-color: #3E3E3E !important;
}

/* ── Divider ── */
hr { border-color: #282828; }

/* ── Last run highlight box ── */
.last-run-box {
    background: linear-gradient(135deg, #1a2e1a, #282828);
    border: 1px solid #1DB954;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── Question card buttons ── */
.question-btn {
    background-color: #282828;
    border: 1px solid #3E3E3E;
    border-radius: 10px;
    padding: 1rem;
    cursor: pointer;
    transition: border-color 0.2s;
    color: #FFFFFF;
    width: 100%;
    text-align: left;
    font-size: 0.9rem;
}
.question-btn:hover { border-color: #1DB954; color: #1DB954; }
</style>
"""
