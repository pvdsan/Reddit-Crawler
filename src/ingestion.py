# ingestion.py

import json
from utils import load_subreddits
import praw
from datetime import datetime
import os

# Load your full list
SUBREDDITS = load_subreddits("../subreddits.txt")

reddit = praw.Reddit(
    client_id="SOaUPFvPmBJx8kOHdLvuBg",
    client_secret="EZhoDA7a4Q007WgtxZz2S7dM_BTS2Q",  
    user_agent="Tech Ideas Scraper",
    username="pvdsan",
    password='Xyzzyspon123!'
)

def scrape_reddit(scrapes_per_subreddit: int) -> str:
    
    output_dir_base = "/data/users4/sdeshpande8/Reddit-Crawler/runs"
    
    #create a directory for the current run
    current_time = datetime.now().strftime("%Y-%m-%d_%H")
    
        ## if a folder with the current time exists, skip the scraping and return the path to the existing folder
    if os.path.exists(os.path.join(output_dir_base, current_time)):
        return os.path.join(output_dir_base, current_time)
    
    os.makedirs(os.path.join(output_dir_base, current_time), exist_ok=True)
    
    #path to the current run
    current_run_path = os.path.join(output_dir_base, current_time)
    
    # Save the Pinecone-formatted results
    raw_scraps_filename = os.path.join(output_dir_base, current_time, f"raw_scrap_results.json")
    

    pinecone_formatted_results = []
    for subreddit in SUBREDDITS:
        print(f"Fetching from r/{subreddit}...")
        try:
            for submission in reddit.subreddit(subreddit).hot(limit=scrapes_per_subreddit):
                title = submission.title or ""
                selftext = submission.selftext or ""
                
                evt = {
                    "_id": submission.id,
                    "subreddit": subreddit,
                    "created_utc": submission.created_utc,
                    "chunk_text": f"{title} {selftext}".strip(),
                    "upvotes": submission.score,
                    "num_comments": submission.num_comments
                }
                pinecone_formatted_results.append(evt)
                        
        except Exception as e:
            print(f"Error fetching from r/{subreddit}: {e}")
            

    
    with open(raw_scraps_filename, "w", encoding="utf-8") as f:
        json.dump(pinecone_formatted_results, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(pinecone_formatted_results)} posts in Pinecone format to {raw_scraps_filename}")
    
    return current_run_path

