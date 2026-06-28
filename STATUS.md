# Project Status

## Current Phase
> Architecture & Planning complete. Ready to build.

---

## What's Built

| Component | Status | Notes |
|---|---|---|
| Architecture document | ✅ Done | ARCHITECTURE.md |
| UI Wireframe | ✅ Done | UI_WIREFRAME.md |
| Requirements | ✅ Done | requirements.txt |
| Env config template | ✅ Done | .env.example |
| Scrapers | ✅ Done | scrapers/app_store.py, play_store.py, reddit_scraper.py, community_scraper.py |
| Pre-filter layer | ✅ Done | pipeline/prefilter.py — tested and passing |
| Storage (SQLite) | ✅ Done | pipeline/storage.py |
| Pipeline runner | ✅ Done | pipeline/runner.py |
| Config | ✅ Done | config.py |
| AI analysis pipeline | ✅ Done | pipeline/extractor.py, scorer.py, synthesizer.py |
| RAG layer | ✅ Done | rag/embedder.py, rag/qa_chain.py — 5 tests passing |
| Streamlit UI | ⏳ Not started | |

---

## Key Decisions

### Trigger Model
**Decision:** Manual-only runs via Streamlit UI button. No weekly cron/scheduling.
**Reason:** This system is an input for a new product opportunity, not ongoing monitoring. Weekly automation adds complexity with no benefit at this stage.

### LLM Stack
**Decision:** Groq (Llama 3.3 70B) for bulk extraction + Claude Haiku for synthesis.
**Reason:** Groq is free and fast enough for processing thousands of reviews in batches. Claude Haiku reserved for final synthesis where reasoning quality matters. Total cost per run ~$0.01.

### LLM Call Count (per run)
| Step | Model | Calls |
|---|---|---|
| Bulk extraction (20 reviews/batch) | Groq | ~45 |
| Opportunity scoring | Groq | 1 |
| Cluster synthesis | Claude Haiku | ~6 |
| Digest summary | Claude Haiku | 1 |
| **Total per run** | | **~53** |
| Per Q&A question | Claude Haiku | +1 |

### Pre-Filtering Strategy
**Decision:** Filter junk reviews before any LLM call to reduce calls by ~50%.
**Reason:** Raw scrapes contain many useless reviews (emoji-only, star-only, spam). Filtering improves signal quality and halves LLM costs.

**Finalized thresholds:**
- Minimum **3 words** (not characters — "Same songs always" = 3 words, real signal)
- Repeated characters: **normalize, don't discard** (typos still carry sentiment)
- Junk character ratio: **>30% non-alpha = discard**
- Near-duplicates: **>80% similarity = keep one, drop rest**
- Language: **English only** for now

### Storage
**Decision:** SQLite to start.
**Reason:** No infrastructure needed, simple to set up, can migrate to PostgreSQL later without changing application code.

### Vector Store
**Decision:** ChromaDB (local).
**Reason:** Free, no cloud infra, runs locally. RAG included from Phase 1 (not later) because it's what makes the system queryable by product managers.

### UI Framework
**Decision:** Streamlit with Spotify color theme.
**Colors:** Primary `#1DB954` (green) · Background `#191414` (black) · Surface `#282828` · Text `#FFFFFF` / `#B3B3B3`

### Source Priority
**Decision:** App Store → Play Store → Reddit → Community
**Reason:** App/Play Store reviews are structured (have star ratings), reliable to scrape, and easiest to validate analysis quality early on.

---

## Pending Decisions
- None currently. All major decisions locked.

---

## Change Log

| Date | Change |
|---|---|
| 2026-06-19 | Project initialized, architecture finalized |
| 2026-06-19 | Pre-filter rules finalized (3-word minimum, normalize repeated chars) |
| 2026-06-19 | Decided manual-only trigger, no weekly scheduling |
| 2026-06-19 | LLM stack locked: Groq + Claude Haiku |
| 2026-06-19 | UI wireframe finalized with Spotify colors |
| 2026-06-19 | Phase 1 built and tested — scrapers, pre-filter, storage, runner |
| 2026-06-19 | Phase 2 built and tested — Groq extractor, opportunity scorer, Claude synthesizer |
| 2026-06-19 | Phase 3 built and tested — ChromaDB embedder, RAG QA chain wired into pipeline |
| 2026-06-19 | Deployment target confirmed: Streamlit Community Cloud (free, zero config) |
| 2026-06-19 | Removed gibberish detection (unreliable without dictionary; 3-word + junk ratio sufficient) |
