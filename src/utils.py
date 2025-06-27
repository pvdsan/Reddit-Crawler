# utils.py

def load_subreddits(file_path="subreddits.txt"):
    """
    Reads a text file of subreddit names (one per line, with or without "r/") 
    and returns a cleaned Python list.
    """
    subs = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Remove leading "r/" if present
            if line.lower().startswith("r/"):
                line = line[2:]
            subs.append(line)
    return subs