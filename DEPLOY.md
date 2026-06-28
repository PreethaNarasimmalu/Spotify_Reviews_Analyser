# Deployment Guide — Streamlit Community Cloud

## Prerequisites
- GitHub account (repo must be public or you must have Streamlit Cloud access)
- Groq API keys (free) — get them at https://console.groq.com

---

## Step 1 — Get Groq API Keys

1. Go to https://console.groq.com
2. Sign up / log in
3. Create up to 5 API keys (Settings → API Keys → Create API Key)
4. Copy each key — you'll need them in Step 3

---

## Step 2 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Connect your GitHub account if not already connected
4. Select:
   - **Repository:** `preethanarasimmalu/spotify_reviews_analyser`
   - **Branch:** `claude/inspiring-ride-ybj65s`
   - **Main file path:** `app.py`
5. Click **"Deploy"**

---

## Step 3 — Add Secrets

After deployment (or before), go to:
**App menu (⋮) → Settings → Secrets**

Paste this, replacing with your real keys:

```toml
GROQ_API_KEY_1 = "gsk_xxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY_2 = "gsk_xxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY_3 = "gsk_xxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY_4 = "gsk_xxxxxxxxxxxxxxxxxxxx"
GROQ_API_KEY_5 = "gsk_xxxxxxxxxxxxxxxxxxxx"
```

You need at least 1 key. More keys = better rate limit handling.

Click **Save** — the app will reboot automatically.

---

## Step 4 — Verify

Once deployed, open the app URL and:
1. Check the sidebar shows sources and timeline filter
2. Click **▶ Run Analysis** — should show progress per source
3. After completion, check **Dashboard** tab for clusters
4. Try a pre-built question in **Ask a Question** tab

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/preethanarasimmalu/spotify_reviews_analyser
cd spotify_reviews_analyser

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Groq API keys

# Run
streamlit run app.py
```

---

## Notes

- **Data persistence:** Streamlit Cloud has ephemeral storage — data resets on redeploy.
  For persistent storage, use a cloud SQLite (Turso) or PostgreSQL (Supabase free tier).
- **ChromaDB:** Also ephemeral on Streamlit Cloud. RAG index rebuilds on each run, which is fine since you control when to run.
- **Cost:** $0 — Groq free tier allows 14,400 requests/day, well above our ~13 calls/run.
