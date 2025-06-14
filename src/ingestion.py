# ingestion.py

import json
from src.utils import load_subreddits, load_config, ensure_runs_dir
import praw
from datetime import datetime
import os

# Load configuration
config = load_config("key.yaml")
if not config:
    raise ValueError("Could not load configuration from key.yaml. Please ensure the file exists and is properly formatted.")

# Load your full list
SUBREDDITS = load_subreddits("subreddits.txt")

# Reddit credentials - must be configured in key.yaml
reddit_config = config.get("reddit", {})
if not all(key in reddit_config for key in ["client_id", "client_secret", "username", "password"]):
    raise ValueError("Reddit configuration is incomplete. Please ensure client_id, client_secret, username, and password are set in key.yaml")

reddit = praw.Reddit(
    client_id=reddit_config["client_id"],
    client_secret=reddit_config["client_secret"],  
    user_agent="Tech Ideas Scraper",
    username=reddit_config["username"],
    password=reddit_config["password"]
)

def scrape_reddit(scrapes_per_subreddit: int) -> str:
    
    # Use the runs directory in the current project
    output_dir_base = ensure_runs_dir()
    
    #create a directory for the current run
    current_time = datetime.now().strftime("%Y-%m-%d_%H_%M")
    
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

