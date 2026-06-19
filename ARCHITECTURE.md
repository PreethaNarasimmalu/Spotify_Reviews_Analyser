# Spotify Review Analysis Engine — Architecture

## Purpose
An AI-powered opportunity discovery engine that analyzes user feedback at scale to surface actionable insights for Spotify's music discovery problem.

**Core Question:** Why do users struggle to discover new music, and what opportunities exist to solve it?

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRIGGER (Weekly or Manual)                  │
│              GitHub Actions Cron  /  Streamlit UI Button        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: DATA INGESTION                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────┐  │
│  │  App Store  │  │ Play Store  │  │  Reddit  │  │Community│  │
│  │  Scraper    │  │  Scraper    │  │  Scraper │  │Scraper  │  │
│  └──────┬──────┘  └──────┬──────┘  └────┬─────┘  └────┬────┘  │
│         └────────────────┴──────────────┴──────────────┘       │
│                             │                                   │
│                    Normalized Review Schema                      │
│         {source, text, rating, date, platform, user_id}        │
│                             │                                   │
│                      PostgreSQL / SQLite                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 2: AI ANALYSIS PIPELINE                 │
│                                                                 │
│   Input: Raw reviews (batched, ~500 at a time)                  │
│                                                                 │
│   Step 1 — Groq (Llama 3.3 70B) — Bulk Extraction              │
│     • Topic tagging (discovery, recommendation, repeat, UX)     │
│     • Frustration signals (what went wrong)                     │
│     • Behavior intent (what user was trying to do)              │
│     • User segment signals (casual / power / audiophile)        │
│     • Sentiment per topic (not just overall)                    │
│                                                                 │
│   Step 2 — Groq — Opportunity Scoring                           │
│     • Frequency score (how often does this theme appear)        │
│     • Intensity score (how strongly do users feel it)           │
│     • Recency score (is it getting worse or better)             │
│     • Signal strength = frequency × intensity × recency         │
│                                                                 │
│   Step 3 — Claude (claude-haiku-4-5) — Insight Synthesis        │
│     • Cluster themes into opportunity areas                     │
│     • Generate hypothesis cards per opportunity                 │
│     • Write weekly digest summary                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: RAG LAYER                           │
│                                                                 │
│   All processed reviews → Embeddings → ChromaDB                │
│                                                                 │
│   Enables semantic search over the full corpus:                 │
│   Query: "users feel trapped in familiar music"                 │
│   Returns: reviews mentioning echo chambers, repeat loops,      │
│            same songs, no variety — even with no word overlap   │
│                                                                 │
│   Powers the Q&A interface in the UI                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: STREAMLIT UI                        │
│                                                                 │
│   ┌──────────────────────────────────────────────────────┐     │
│   │  Sidebar: Source filter │ Date range │ Segment filter│     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                 │
│   Tab 1 — Run Analysis                                          │
│     [▶ Run Analysis] button → triggers full pipeline            │
│     Live progress bar → completion summary                      │
│                                                                 │
│   Tab 2 — Opportunity Dashboard                                 │
│     • Top opportunity clusters (bar chart by signal strength)  │
│     • Trend over time (is the problem growing?)                 │
│     • Segment breakdown (who feels it most?)                   │
│     • Hypothesis cards with supporting quote count             │
│                                                                 │
│   Tab 3 — Ask a Question (RAG Q&A)                              │
│     Pre-built question cards:                                   │
│     ┌──────────────────────────────────┐                       │
│     │ Why do users struggle to         │                       │
│     │ discover new music?              │                       │
│     └──────────────────────────────────┘                       │
│     ┌──────────────────────────────────┐                       │
│     │ What causes repetitive listening?│                       │
│     └──────────────────────────────────┘                       │
│     ... (all 6 questions as clickable cards) ...               │
│     + Custom question input box                                │
│                                                                 │
│     Answer format:                                             │
│     • Structured response grounded in real reviews             │
│     • Signal strength (% of reviews mentioning this)          │
│     • Top 3-5 supporting quotes with source + date            │
│     • Opportunity hypothesis card                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Build Phases

### Phase 1 — Scrapers (Week 1)
- App Store scraper (app-store-scraper)
- Play Store scraper (google-play-scraper)
- Reddit scraper (PRAW — r/spotify, r/musicrecommendations, r/spotifyplaylist)
- Spotify Community scraper (BeautifulSoup)
- Normalized data storage (SQLite to start)

**Priority order:** App Store → Play Store → Reddit → Community

### Phase 2 — AI Analysis Pipeline (Week 1-2)
- Groq integration for bulk extraction
- Structured JSON output per review (topics, signals, segment, sentiment)
- Opportunity scoring algorithm
- Claude integration for synthesis and digest

### Phase 3 — RAG Layer (Week 2)
- sentence-transformers for embeddings
- ChromaDB for vector storage
- Retrieval function: query → top-K relevant reviews
- RAG chain: query + retrieved reviews → Claude answer

### Phase 4 — Streamlit UI (Week 2-3)
- Run Analysis tab with manual trigger button
- Opportunity Dashboard with Plotly charts
- Q&A interface with pre-built question cards
- GitHub Actions cron for weekly automated runs

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Scrapers | Python (app-store-scraper, google-play-scraper, PRAW) | Purpose-built libraries |
| Storage | SQLite → PostgreSQL | Simple start, easy upgrade |
| Bulk AI | Groq (Llama 3.3 70B) | Free, fast, handles volume |
| Synthesis AI | Claude (claude-haiku-4-5) | Better reasoning for summaries |
| Vector Store | ChromaDB | Free, local, no infra needed |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Fast, free, good quality |
| UI | Streamlit | Fastest path to interactive UI |
| Charts | Plotly | Interactive, looks good in Streamlit |
| Scheduling | GitHub Actions (weekly cron) | Already in repo, free |

---

## Key Design Decisions

1. **Weekly batch + manual trigger** — No real-time infra needed; GitHub Actions cron for automation, Streamlit button for on-demand runs
2. **Groq for volume, Claude for quality** — Groq handles thousands of reviews cheaply; Claude writes the final synthesis
3. **RAG from Phase 1** — Not an afterthought; it's what makes the system answerable by product managers
4. **SQLite first** — Can migrate to PostgreSQL later without changing application code
5. **Source priority** — App Store and Play Store first (structured, rated, reliable); Reddit second (rich discussion); Community last (lower volume)

---

## Output Per Run

```
outputs/
  YYYY-MM-DD/
    raw_reviews.json          ← all scraped reviews this run
    analyzed_reviews.json     ← reviews with AI-extracted tags
    opportunity_clusters.json ← grouped themes with scores
    hypothesis_cards.json     ← opportunity framing per cluster
    weekly_digest.md          ← Claude-generated summary
```

---

## The 6 Questions This System Answers

| Question | How |
|---|---|
| Why do users struggle to discover new music? | RAG Q&A + topic cluster: "discovery friction" |
| What are the most common frustrations with recommendations? | Frustration signal extraction + frequency ranking |
| What listening behaviors are users trying to achieve? | Intent classification per review |
| What causes repetitive listening? | Topic cluster: "echo chamber / repeat loop" |
| Which user segments experience different discovery challenges? | Segment tagging + cross-segment comparison |
| What unmet needs emerge consistently? | Opportunity scoring across all clusters |
