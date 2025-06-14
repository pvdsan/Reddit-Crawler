# pipeline_inventory.py
# Analysis of current Reddit scraper pipeline functions

PIPELINE_FUNCTIONS = {
    "data_ingestion": {
        "scrape_reddit": {
            "location": "src/ingestion.py",
            "description": "Scrape Reddit posts from configured subreddits",
            "inputs": ["scrapes_per_subreddit: int"],
            "outputs": ["current_run_path: str"],
            "dependencies": ["Reddit API", "subreddits.txt"]
        },
        "load_subreddits": {
            "location": "src/utils.py", 
            "description": "Load subreddit list from configuration file",
            "inputs": ["file_path: str"],
            "outputs": ["List[str]"],
            "dependencies": ["subreddits.txt"]
        }
    },
    
    "data_processing": {
        "create_vector_database": {
            "location": "src/create_vector_database.py",
            "description": "Create vector embeddings and upload to Pinecone",
            "inputs": ["current_run_path: str", "batch_size: int", "index_name: str"],
            "outputs": ["success: bool"],
            "dependencies": ["Pinecone API", "raw_scrap_results.json"]
        }
    },
    
    "analysis": {
        "search_vector_db": {
            "location": "src/search_vector_db.py", 
            "description": "Perform semantic search on vector database",
            "inputs": ["index_name: str", "query_file_path: str", "current_run_path: str", "top_k: int"],
            "outputs": ["vector_search_results.txt"],
            "dependencies": ["Pinecone API", "Ideation_Query.txt"]
        },
        "return_gemini_response": {
            "location": "src/gemini_retrieval.py",
            "description": "Generate AI insights from search results", 
            "inputs": ["query_file_path: str", "current_run_path: str", "model: str"],
            "outputs": ["gemini_response.txt"],
            "dependencies": ["Gemini API", "vector_search_results.txt"]
        }
    },
    
    "utilities": {
        "load_config": {
            "location": "src/utils.py",
            "description": "Load configuration from YAML file",
            "inputs": ["config_path: str"],
            "outputs": ["Dict[str, Any]"],
            "dependencies": ["key.yaml"]
        },
        "ensure_runs_dir": {
            "location": "src/utils.py",
            "description": "Create and return runs directory path",
            "inputs": [],
            "outputs": ["str"],
            "dependencies": []
        }
    }
}

# Main pipeline workflow
PIPELINE_WORKFLOW = [
    "load_config() -> configuration",
    "scrape_reddit(scrapes_per_subreddit) -> run_path", 
    "create_vector_database(run_path) -> vector_db",
    "search_vector_db(query, run_path) -> search_results",
    "return_gemini_response(query, run_path) -> ai_insights"
]

# Current file structure
CURRENT_FILES = {
    "src/main.py": "Main orchestration script",
    "src/ingestion.py": "Reddit data collection", 
    "src/create_vector_database.py": "Vector embedding creation",
    "src/search_vector_db.py": "Semantic search implementation",
    "src/gemini_retrieval.py": "AI analysis integration",
    "src/utils.py": "Utility functions",
    "key.yaml": "API configuration",
    "subreddits.txt": "Target subreddits list",
    "Ideation_Query.txt": "Search queries",
    "requirements.txt": "Dependencies"
} 