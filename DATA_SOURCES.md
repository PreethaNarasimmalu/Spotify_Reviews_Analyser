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

## 3. Spotify Community Forum

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
| 1 | App Store | Structured, rated, reliable API, no credentials |
| 2 | Play Store | Structured, rated, reliable API, no credentials |
| 3 | Community | Explicit feature requests = strong intent signal, no credentials |

---

## What We Do NOT Scrape

- Reddit — removed to reduce complexity and avoid API credential setup
- Twitter/X — API now paid
- Non-English sources — filtered out in pre-filter layer for now
