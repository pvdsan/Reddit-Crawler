from ingestion import scrape_reddit
from create_vector_database import create_vector_database
from search_vector_db import search_vector_db
from gemini_retrieval import return_gemini_response
import os
from utils import get_project_root

def main():
    
    # Use relative paths that work on any system
    project_root = get_project_root()
    query_file_path = os.path.join(project_root, "Ideation_Query.txt")
    
    current_run_path = scrape_reddit(scrapes_per_subreddit=100)
    
    # check if vector search results already exist. If yes then skip creation of vector database and search
    if os.path.exists(os.path.join(current_run_path, "vector_search_results.txt")):
        print("Vector search results already exist. Skipping vector database creation and search.")
    else:
        create_vector_database(current_run_path, batch_size=95, index_name="tech-ideas-py")
        search_vector_db(index_name="tech-ideas-py", query_file_path=query_file_path, current_run_path=current_run_path, top_k = 100)
    
    return_gemini_response(query_file_path=query_file_path, current_run_path=current_run_path, model="gemini-2.0-flash-exp")
    
if __name__ == "__main__":
    main()