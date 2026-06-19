# Streamlit UI — Layout & Wireframe

## Overall Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎵 Spotify Review Analysis Engine                    [Spotify Logo] │
├──────────────┬──────────────────────────────────────────────────────┤
│              │                                                       │
│   SIDEBAR    │              MAIN CONTENT AREA                       │
│              │                                                       │
│  Filters     │   [ Run Analysis ] [ Dashboard ] [ Ask a Question ]  │
│  ─────────   │   ─────────────────────────────────────────────────  │
│              │                                                       │
│  Sources     │              (Tab content below)                     │
│  ☑ App Store │                                                       │
│  ☑ Play Store│                                                       │
│  ☑ Reddit    │                                                       │
│  ☑ Community │                                                       │
│              │                                                       │
│  Date Range  │                                                       │
│  From: ____  │                                                       │
│  To:   ____  │                                                       │
│              │                                                       │
│  Segment     │                                                       │
│  ○ All Users │                                                       │
│  ○ Casual    │                                                       │
│  ○ Power     │                                                       │
│  ○ Audiophile│                                                       │
│              │                                                       │
│  Last Run:   │                                                       │
│  2026-06-19  │                                                       │
│  847 reviews │                                                       │
│              │                                                       │
└──────────────┴──────────────────────────────────────────────────────┘
```

---

## Tab 1 — Run Analysis

```
┌─────────────────────────────────────────────────────────────────────┐
│  Run Analysis                                                        │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  Last analysis run: 2026-06-19 · 847 reviews collected              │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │   This will scrape reviews from all selected sources,        │  │
│  │   run AI analysis, and update the dashboard and Q&A.         │  │
│  │                                                               │  │
│  │              [ ▶  Run Full Analysis ]                         │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ── While running ──────────────────────────────────────────────    │
│                                                                      │
│  ✅ App Store scraper        → 312 reviews collected                 │
│  ✅ Play Store scraper       → 289 reviews collected                 │
│  🔄 Reddit scraper           → Fetching...                           │
│  ⏳ Community scraper        → Waiting                               │
│  ⏳ AI Analysis Pipeline     → Waiting                               │
│  ⏳ Building RAG index       → Waiting                               │
│                                                                      │
│  [████████████░░░░░░░░░░░░░░░░]  40%                                 │
│                                                                      │
│  ── On completion ──────────────────────────────────────────────    │
│                                                                      │
│  ✅ Analysis complete!                                                │
│  📊 1,024 reviews analysed · 6 opportunity clusters found            │
│  🔍 RAG index updated · Ready to answer questions                    │
│                                                                      │
│  → Go to Dashboard   → Ask a Question                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tab 2 — Opportunity Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  Opportunity Dashboard                                               │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │  Total Reviews  │  │  Clusters Found │  │  Top Signal     │     │
│  │     1,024       │  │       6         │  │  Echo Chamber   │     │
│  │  across 4 src   │  │                 │  │  Score: 87/100  │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                      │
│  Opportunity Clusters by Signal Strength                             │
│  ───────────────────────────────────────                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  Echo Chamber / Repeat Loop        ████████████████████  87  │  │
│  │  Recommendation Mismatch           ███████████████░░░░░  71  │  │
│  │  Discovery Surface UX              ████████████░░░░░░░░  63  │  │
│  │  Genre Tunnel Vision               ██████████░░░░░░░░░░  55  │  │
│  │  Cross-Language Discovery          ███████░░░░░░░░░░░░░  41  │  │
│  │  Social Discovery Gap              █████░░░░░░░░░░░░░░░  33  │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Trend Over Time — Echo Chamber mentions                             │
│  ───────────────────────────────────────                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                              ╭──╮             │  │
│  │                                         ╭───╯  │             │  │
│  │                               ╭─────────╯      │             │  │
│  │  ─────────────────────────────╯                │             │  │
│  │  Jan    Feb    Mar    Apr    May    Jun         │             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Segment Breakdown — Who feels it most?                              │
│  ───────────────────────────────────────                             │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │
│  │ Casual Users   │  │ Power Users    │  │ Audiophiles    │         │
│  │ Top issue:     │  │ Top issue:     │  │ Top issue:     │         │
│  │ Same songs on  │  │ Algo doesn't  │  │ Too mainstream │         │
│  │ auto-play      │  │ update taste   │  │ recommendations│         │
│  │ 43% mentions   │  │ 61% mentions   │  │ 78% mentions   │         │
│  └────────────────┘  └────────────────┘  └────────────────┘         │
│                                                                      │
│  Opportunity Hypothesis Cards                                        │
│  ───────────────────────────────────────                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  🔴 HIGH SIGNAL — Echo Chamber                                │  │
│  │                                                               │  │
│  │  "Long-term users feel trapped in familiar content.           │  │
│  │  The algorithm reinforces existing taste instead of           │  │
│  │  gradually expanding it."                                     │  │
│  │                                                               │  │
│  │  362 reviews · Score 87 · Trending ↑                         │  │
│  │  Segment: Power users (61%) + Audiophiles (78%)              │  │
│  │                                                               │  │
│  │  [ View Supporting Quotes ]  [ Explore in Q&A ]              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  🟠 MEDIUM SIGNAL — Recommendation Mismatch          ...      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tab 3 — Ask a Question (RAG Q&A)

```
┌─────────────────────────────────────────────────────────────────────┐
│  Ask a Question                                                      │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  Pre-built questions — click to ask instantly                        │
│                                                                      │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐ │
│  │ Why do users struggle to     │  │ What are the most common     │ │
│  │ discover new music?          │  │ frustrations with            │ │
│  │                              │  │ recommendations?             │ │
│  └──────────────────────────────┘  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐ │
│  │ What listening behaviors are │  │ What causes users to         │ │
│  │ users trying to achieve?     │  │ repeatedly listen to the     │ │
│  │                              │  │ same content?                │ │
│  └──────────────────────────────┘  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐ │
│  │ Which user segments face     │  │ What unmet needs emerge      │ │
│  │ different discovery          │  │ consistently across reviews? │ │
│  │ challenges?                  │  │                              │ │
│  └──────────────────────────────┘  └──────────────────────────────┘ │
│                                                                      │
│  Or ask your own question:                                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Type your question here...                          [ Ask ]  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ── Answer ─────────────────────────────────────────────────────    │
│                                                                      │
│  Q: Why do users struggle to discover new music?                     │
│  Based on 1,024 reviews across App Store, Play Store, and Reddit:   │
│                                                                      │
│  Users primarily struggle because the algorithm reinforces           │
│  existing listening patterns rather than gradually expanding         │
│  taste boundaries. 62% of relevant reviews describe a feeling        │
│  of being "stuck" or in a "bubble."                                  │
│                                                                      │
│  Key reasons identified:                                             │
│  1. Discover Weekly recycles known artists (41% of mentions)        │
│  2. Radio mode amplifies one mood/genre indefinitely (28%)          │
│  3. No clear path to intentional exploration (19%)                  │
│  4. New releases drowned out by familiar content (12%)              │
│                                                                      │
│  Signal strength: 87/100 · Trending ↑ over last 3 months            │
│                                                                      │
│  Supporting Quotes                                                   │
│  ─────────────────                                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ "Every single week Discover Weekly gives me artists I         │  │
│  │  already follow. It's not discovering anything."              │  │
│  │  — Reddit · r/spotify · 3 days ago                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ "The algorithm thinks I only like sad indie music because     │  │
│  │  I listened to it once during a breakup."                     │  │
│  │  — App Store · ★★☆☆☆ · 1 week ago                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ "I've been using Spotify for 6 years and my Wrapped is        │  │
│  │  basically identical every year. Something is wrong."         │  │
│  │  — Play Store · ★★★☆☆ · 2 weeks ago                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Opportunity Hypothesis                                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  💡 Users want intentional taste expansion, not just          │  │
│  │  comfort-zone reinforcement. An AI-guided "discovery mode"    │  │
│  │  that explicitly signals "this is new territory" could        │  │
│  │  reduce echo chamber frustration significantly.               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Navigation Flow

```
Landing (Tab 1: Run Analysis)
    │
    ├── [▶ Run Analysis] clicked
    │       └── Progress → Completion → links to Tab 2 & Tab 3
    │
    ├── Tab 2: Dashboard
    │       ├── [View Supporting Quotes] → expands quote list inline
    │       └── [Explore in Q&A] → switches to Tab 3 with that cluster pre-loaded
    │
    └── Tab 3: Ask a Question
            ├── Click pre-built question card → auto-runs query
            └── Type custom question → [Ask] → answer renders below
```
