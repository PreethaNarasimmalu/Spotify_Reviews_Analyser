import praw
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_SUBREDDITS, REDDIT_SEARCH_TERMS


def scrape_reddit(days: int = 30, max_posts: int = 100) -> list[dict]:
    print(f"[Reddit] Scraping last {days} days...")
    cutoff = datetime.now() - timedelta(days=days)

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    collected = []

    for subreddit_name in REDDIT_SUBREDDITS:
        subreddit = reddit.subreddit(subreddit_name)

        for term in REDDIT_SEARCH_TERMS:
            try:
                for post in subreddit.search(term, sort="new", time_filter="month", limit=max_posts // len(REDDIT_SEARCH_TERMS)):
                    post_date = datetime.fromtimestamp(post.created_utc)
                    if post_date < cutoff:
                        continue

                    if post.selftext and post.selftext.strip() not in ("[removed]", "[deleted]", ""):
                        collected.append({
                            "source": "reddit",
                            "platform": "reddit",
                            "text": f"{post.title}. {post.selftext}".strip(),
                            "rating": None,
                            "date": post_date.isoformat(),
                            "user_id": str(post.author) if post.author else "deleted",
                            "title": post.title,
                        })

                    post.comments.replace_more(limit=0)
                    for comment in post.comments.list()[:10]:
                        c_date = datetime.fromtimestamp(comment.created_utc)
                        if c_date < cutoff:
                            continue
                        if comment.body and comment.body not in ("[removed]", "[deleted]"):
                            collected.append({
                                "source": "reddit",
                                "platform": "reddit",
                                "text": comment.body,
                                "rating": None,
                                "date": c_date.isoformat(),
                                "user_id": str(comment.author) if comment.author else "deleted",
                                "title": "",
                            })
            except Exception as e:
                print(f"[Reddit] Error on r/{subreddit_name} '{term}': {e}")
                continue

    print(f"[Reddit] {len(collected)} posts/comments collected")
    return collected
