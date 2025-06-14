# utils.py
import yaml
import os

def load_subreddits(file_path="subreddits.txt"):
    """
    Reads a text file of subreddit names (one per line, with or without "r/") 
    and returns a cleaned Python list.
    """
    # If running from src directory, look in parent directory
    if not os.path.exists(file_path) and os.path.basename(os.getcwd()) == 'src':
        file_path = os.path.join('..', file_path)
    
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

def load_config(config_path="key.yaml"):
    """
    Load configuration from YAML file
    """
    # If running from src directory, look in parent directory
    if not os.path.exists(config_path) and os.path.basename(os.getcwd()) == 'src':
        config_path = os.path.join('..', config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found!")
        return None
    except yaml.YAMLError as e:
        print(f"Error reading YAML file: {e}")
        return None

def get_project_root():
    """
    Get the project root directory (where this script is run from)
    """
    current_dir = os.getcwd()
    # If we're in src directory, go up one level
    if os.path.basename(current_dir) == 'src':
        return os.path.dirname(current_dir)
    return current_dir

def get_runs_dir():
    """
    Get the runs directory path
    """
    return os.path.join(get_project_root(), "runs")

def ensure_runs_dir():
    """
    Ensure the runs directory exists
    """
    runs_dir = get_runs_dir()
    os.makedirs(runs_dir, exist_ok=True)
    return runs_dir