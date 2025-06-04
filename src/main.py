from ingestion import scrape_reddit
from create_vector_database import create_vector_database
from search_vector_db import search_vector_db
from gemini_retrieval import return_gemini_response

def main():
    current_run_path = scrape_reddit( scrapes_per_subreddit=10)
    create_vector_database(current_run_path, batch_size=95, index_name="tech-ideas-py")
    search_vector_db(index_name="tech-ideas-py", query_file_path="../Ideation_Query.txt", current_run_path=current_run_path, top_k = 10)
    return_gemini_response(query_file_path="../Ideation_Query.txt", current_run_path=current_run_path)
    
    
    
    
    

if __name__ == "__main__":
    main()