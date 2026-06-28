# Data Sources

All sources are public. No login or paid API required except Reddit (free API key).

---

## 1. Apple App Store

**App URL:** https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580
**App ID:** `324684580`
**Library:** `app-store-scraper`
**How it works:** Hits Apple's internal review JSON API (not the HTML page) using the app ID.
**Credentials needed:** None
**Data returned:** review text, star rating, date, username, review title

---

## 2. Google Play Store

**App URL:** https://play.google.com/store/apps/details?id=com.spotify.music
**Package ID:** `com.spotify.music`
**Library:** `google-play-scraper`
**How it works:** Calls Google Play's internal review API endpoints (same ones the browser hits when scrolling reviews), not the HTML page.
**Credentials needed:** None
**Data returned:** review text, star rating (1-5), date, username

---

## 3. Reddit

**Subreddits scraped:**
- https://www.reddit.com/r/spotify
- https://www.reddit.com/r/musicrecommendations
- https://www.reddit.com/r/spotifyplaylist

**Search terms used:** `discover weekly`, `recommendation`, `same songs`, `music discovery`, `algorithm`, `new music`, `playlist`, `repeat`

**Library:** `PRAW` (Python Reddit API Wrapper)
**How it works:** Uses the official Reddit API to search posts and fetch top comments per post.
**Credentials needed:** ✅ Free Reddit API key
  - Create app at: https://www.reddit.com/prefs/apps
  - Add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` to `.env`
**Data returned:** post title + body text, comment text, date, username

---

## 4. Spotify Community Forum

**Primary source (Ideas board):**
https://community.spotify.com/t5/Ideas/ct-p/newideas
→ Users explicitly request features and voice product frustrations. Highest signal quality.

**Search pages also scraped:**
- https://community.spotify.com/t5/forums/searchpage/tab/message?q=music+discovery&search_type=thread
- https://community.spotify.com/t5/forums/searchpage/tab/message?q=recommendations&search_type=thread
- https://community.spotify.com/t5/forums/searchpage/tab/message?q=same+songs&search_type=thread
- https://community.spotify.com/t5/forums/searchpage/tab/message?q=discover+weekly&search_type=thread

**Library:** `BeautifulSoup` + `requests` (HTML scraping)
**How it works:** Fetches public forum HTML pages and parses post content from `lia-message-body-content` divs.
**Credentials needed:** None
**Data returned:** post text, date (approximated to run date), no rating
**Fragility note:** CSS class names can change if Spotify updates their forum theme. Most fragile source — monitor if it stops returning results.

---

## Source Priority

| Priority | Source | Why |
|---|---|---|
| 1 | App Store | Structured, rated, reliable API |
| 2 | Play Store | Structured, rated, reliable API |
| 3 | Reddit | Rich discussion, high volume, best signal-to-noise after filtering |
| 4 | Community | Explicit feature requests = strong intent signal, but lower volume |

---

## What We Do NOT Scrape

- Twitter/X — API now paid, too expensive for this use case
- Trustpilot, G2, Capterra — Spotify not primarily reviewed there
- Non-English sources — filtered out in pre-filter layer for now
