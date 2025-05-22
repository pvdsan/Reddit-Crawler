# ingestion.py

import json
from utils import load_subreddits
import praw

# Load your full list
SUBREDDITS = load_subreddits("subreddits.txt")

reddit = praw.Reddit(
    client_id="SOaUPFvPmBJx8kOHdLvuBg",
    client_secret="EZhoDA7a4Q007WgtxZz2S7dM_BTS2Q",  
    user_agent="Tech Ideas Scraper",
    username="pvdsan",
    password='Xyzzyspon123!'
)
print(reddit.user.me())

def is_request(text: str) -> bool:
    txt = text.lower()
    return True

def main():
    results = []
    for subreddit in SUBREDDITS:
        print(f"Fetching from r/{subreddit}...")
        try:
            for submission in reddit.subreddit(subreddit).new(limit=100):
                combined = submission.title + " " + (submission.selftext or "")
                if is_request(combined):
                    evt = {
                        "id": submission.id,
                        "subreddit": subreddit,
                        "created_utc": submission.created_utc,
                        "title": submission.title,
                        "body": submission.selftext,
                        "upvotes": submission.score,
                        "num_comments": submission.num_comments
                    }
                    results.append(evt)
        except Exception as e:
            print(f"Error fetching from r/{subreddit}: {e}")
    with open("results2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(results)} posts to results3.json")

if __name__ == "__main__":
    main()
