import os
from datetime import datetime
import json
import praw
import yaml

with open("secrets.yaml", 'r') as stream:
    keys = yaml.safe_load(stream)

def get_comments_text(submission, max_comments=5):
    """
    Extract comments from a Reddit submission.
    Returns a string containing all comment text.
    """
    comments_text = []
    try:
        # Expand more comments to get deeper nested comments
        submission.comments.replace_more(limit=0)
        
        # Get all comments (flattened list)
        all_comments = submission.comments.list()
        
        # Limit the number of comments to avoid extremely long text
        for comment in all_comments[:max_comments]:
            if hasattr(comment, 'body') and comment.body != '[deleted]' and comment.body != '[removed]':
                comments_text.append(comment.body)
                
    except Exception as e:
        print(f"Error fetching comments: {e}")
        
    return " ".join(comments_text)


def scrape_reddit_dynamic(topic: str, subreddit_limit: int = 3, post_limit: int = 100):
    """
    Fetches subreddits matching the given topic and returns a list sorted by subscriber count.
    """
    reddit = praw.Reddit(
        client_id=keys['REDDIT_CLIENT_ID'],
        client_secret=keys['REDDIT_CLIENT_SECRET'],
        user_agent=keys['REDDIT_USER_AGENT'],
        username=keys['REDDIT_USERNAME'],
        password=keys['REDDIT_PASSWORD']
    )
    
    
    output_dir_base = "runs"
    
    # Create a directory for the current run, named by city and date.
    date_str = datetime.now().strftime("%m_%d")
    run_name = f"{topic.lower()}_{date_str}"
    current_run_path = os.path.join(output_dir_base, run_name)
    
    # If a folder for the current run exists, skip scraping and return the path.
    if os.path.exists(current_run_path):
        print(f"Run directory '{current_run_path}' already exists. Skipping scraping.")
        return current_run_path
    
    os.makedirs(current_run_path, exist_ok=True)
    
    # Save the Pinecone-formatted results
    raw_scraps_filename = os.path.join(current_run_path, "raw_scrap_results.json")    


    pinecone_formatted_results = []
    
    subs = reddit.subreddits.search(query=topic, limit=subreddit_limit)

    for subreddit in subs:
        try:
            for submission in reddit.subreddit(subreddit.display_name).hot(limit=post_limit):
                title = submission.title or ""
                selftext = submission.selftext or ""
                comments_text = get_comments_text(submission)
                
                evt = { 
                    "_id": submission.id,
                    "subreddit": subreddit.display_name,
                    "created_utc": submission.created_utc,
                    "chunk_text": f"{title} {selftext} {comments_text}".strip(),
                    "upvotes": submission.score,
                    "num_comments": submission.num_comments
                }
                pinecone_formatted_results.append(evt)
                        
        except Exception as e:
            print(f"Error fetching from r/{subreddit.display_name}: {e}")

    with open(raw_scraps_filename, "w", encoding="utf-8") as f:
        json.dump(pinecone_formatted_results, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(pinecone_formatted_results)} posts in Pinecone format to {raw_scraps_filename}")
    
    return current_run_path

