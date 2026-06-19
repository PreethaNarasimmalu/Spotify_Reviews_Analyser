# Spotify Review Analysis Engine — Architecture

## Purpose
An AI-powered opportunity discovery engine that analyzes user feedback at scale to surface actionable insights for Spotify's music discovery problem.

**Core Question:** Why do users struggle to discover new music, and what opportunities exist to solve it?

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRIGGER (Manual Only)                       │
│                 Streamlit UI — "Run Analysis" Button            │
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
│                    Raw Reviews (unfiltered)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 2: PRE-FILTERING                      │
│                                                                 │
│   Hard Filters (auto-discard):                                  │
│   • No text — star rating only or empty body                    │
│   • Less than 3 words                                           │
│   • Only emoji — entire review is emoji                         │
│   • Junk/gibberish — >30% non-alphabetic characters             │
│   • No real words detected                                      │
│   • Non-English reviews (for now)                               │
│   • Spam — same review text across multiple users               │
│   • Near-duplicates — >80% similarity, keep one drop rest       │
│                                                                 │
│   Normalization (keep but clean):                               │
│   • Repeated characters normalized → "plssssss" → "pls"        │
│                                                                 │
│   Soft Filters (deprioritize, don't discard):                   │
│   • Single generic sentence with high rating                    │
│   • Very generic praise with no specific feedback               │
│                                                                 │
│   Expected outcome: ~40-60% of raw reviews dropped             │
│   Filter log saved separately for auditing                      │
│                                                                 │
│   UI shows after run:                                           │
│   ✅ 2,041 scraped → 🗑️ 1,102 filtered → 📊 939 analysed       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                PHASE 3: AI ANALYSIS PIPELINE                    │
│                                                                 │
│   Input: ~900 clean reviews                                     │
│                                                                 │
│   Step 1 — Groq (Llama 3.3 70B) — Bulk Extraction              │
│     • Batch size: 20 reviews per call                           │
│     • ~45 Groq calls total (down from ~100 without filtering)   │
│     • Extracts per review:                                      │
│       - Topic tags (discovery, recommendation, repeat, UX)      │
│       - Frustration signals (what went wrong)                   │
│       - Behavior intent (what user was trying to do)            │
│       - User segment signal (casual / power / audiophile)       │
│       - Per-topic sentiment (not just overall)                  │
│                                                                 │
│   Step 2 — Groq — Opportunity Scoring                           │
│     • 1 call to score and rank all clusters                     │
│     • Signal strength = frequency × intensity × recency         │
│                                                                 │
│   Step 3 — Claude (claude-haiku-4-5) — Insight Synthesis        │
│     • 1 call per opportunity cluster (~6 clusters = 6 calls)    │
│     • Generates hypothesis card per cluster                     │
│     • 1 final call for full digest narrative                    │
│                                                                 │
│   Total LLM calls per run:                                      │
│   ┌────────────────────────────────────────────────────────┐    │
│   │ Groq bulk extraction    ~45 calls                      │    │
│   │ Groq opportunity score   1 call                        │    │
│   │ Claude cluster synthesis 6 calls                       │    │
│   │ Claude digest            1 call                        │    │
│   │ ─────────────────────────────────                      │    │
│   │ Total per run           ~53 calls                      │    │
│   │ Per Q&A question        +1 Claude call                 │    │
│   │ ─────────────────────────────────                      │    │
│   │ Cost: ~$0.01 total (Claude Haiku)                      │    │
│   │ Groq: free tier (14,400 req/day — well within limit)   │    │
│   └────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: RAG LAYER                           │
│                                                                 │
│   Clean reviews → Embeddings (sentence-transformers)           │
│   → Stored in ChromaDB (local vector store)                    │
│                                                                 │
│   On Q&A query:                                                 │
│   User question → embed → retrieve top-K relevant reviews      │
│   → feed to Claude Haiku → structured answer with quotes       │
│                                                                 │
│   Why RAG from Phase 1 (not later):                            │
│   It's what makes the system answerable — product managers     │
│   can ask natural language questions and get evidence-backed   │
│   answers from real user reviews, not LLM hallucination        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 5: STREAMLIT UI                        │
│                  (Spotify Colors — #1DB954 / #191414)           │
│                                                                 │
│   Tab 1 — Run Analysis                                          │
│   ┌──────────────────────────────────────────────────────┐     │
│   │  LAST RUN HIGHLIGHTS                                 │     │
│   │  19 Jun 2026 · 939 reviews · 6 opportunities found  │     │
│   │  🔴 Echo Chamber (87) · 🟠 Rec Mismatch (71)         │     │
│   │                          [ View Full Last Run ]      │     │
│   └──────────────────────────────────────────────────────┘     │
│   ┌──────────────────────────────────────────────────────┐     │
│   │  Sources: ☑ App Store ☑ Play Store ☑ Reddit ☑ Comm  │     │
│   │  Timeline: [ Last 30 days ▾ ] (7d / 30d / 90d / Custom)   │
│   │                  [ ▶ Run Analysis ]                  │     │
│   └──────────────────────────────────────────────────────┘     │
│                                                                 │
│   Tab 2 — Opportunity Dashboard                                 │
│     • Metric cards (total reviews, clusters, top signal)        │
│     • Opportunity clusters bar chart (signal strength)          │
│     • Trend over time line chart                                │
│     • Segment breakdown cards (casual / power / audiophile)    │
│     • Hypothesis cards per cluster with quotes                  │
│                                                                 │
│   Tab 3 — Ask a Question (RAG Q&A)                              │
│     • 6 pre-built question cards (click to ask instantly)       │
│     • Custom question input box                                 │
│     • Answer: narrative + % signal + top quotes + hypothesis    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Build Phases

### Phase 1 — Scrapers
- App Store scraper (app-store-scraper)
- Play Store scraper (google-play-scraper)
- Reddit scraper (PRAW — r/spotify, r/musicrecommendations, r/spotifyplaylist)
- Spotify Community scraper (BeautifulSoup)
- Raw storage in SQLite

**Priority order:** App Store → Play Store → Reddit → Community

### Phase 2 — Pre-Filter Layer
- Hard filter engine (word count, junk detection, duplicate check)
- Character normalization (repeated chars)
- Language detection
- Filter audit log

### Phase 3 — AI Analysis Pipeline
- Groq integration — batched extraction (20 reviews/call)
- Structured JSON output per review
- Opportunity scoring
- Claude integration — synthesis + digest

### Phase 4 — RAG Layer
- sentence-transformers embeddings (all-MiniLM-L6-v2)
- ChromaDB vector store
- Retrieval + answer generation chain

### Phase 5 — Streamlit UI
- Spotify color theme
- Tab 1: Run Analysis with last-run highlights + timeline filter
- Tab 2: Opportunity Dashboard
- Tab 3: RAG Q&A with pre-built question cards

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Scrapers | app-store-scraper, google-play-scraper, PRAW, BeautifulSoup | Purpose-built |
| Storage | SQLite | Simple, no infra, easy to migrate later |
| Pre-filter | Python (langdetect, difflib) | Lightweight, no API calls needed |
| Bulk AI | Groq (Llama 3.3 70B) | Free, fast, handles volume |
| Synthesis AI | Claude (claude-haiku-4-5) | Better reasoning, ~$0.01/run |
| Vector Store | ChromaDB | Free, local, no infra needed |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Fast, free, good quality |
| UI | Streamlit | Fast to build, supports interactive components |
| Charts | Plotly | Interactive charts in Streamlit |

---

## Trigger Model
**Manual only** — no scheduled/weekly runs. This system is an input for a new product opportunity, not ongoing monitoring. Run it when you need fresh data before research sessions or presentations.

---

## Pre-Filter Thresholds (Finalized)
| Rule | Threshold | Rationale |
|---|---|---|
| Minimum word count | 3 words | "Same songs always" = 3 words, carries real signal |
| Repeated characters | Normalize, don't discard | Typos still carry sentiment |
| Junk character ratio | >30% non-alpha = discard | Emoji-only reviews useless |
| Near-duplicate | >80% similarity = drop one | Deduplication |
| Language | English only (for now) | Model accuracy |

---

## Output Per Run

```
outputs/
  YYYY-MM-DD/
    raw_reviews.json          ← all scraped reviews
    filter_log.json           ← what was dropped and why
    analyzed_reviews.json     ← reviews with AI-extracted tags
    opportunity_clusters.json ← grouped themes with scores
    hypothesis_cards.json     ← opportunity framing per cluster
    digest.md                 ← Claude-generated summary
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
