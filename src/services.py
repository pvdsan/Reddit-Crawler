from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import uvicorn
from .ingestion import scrape_reddit
from .create_vector_database import create_vector_database
from .search_vector_db import search_vector_db
#from gemini_retrieval import return_gemini_response

app = FastAPI()

class FetchSearchRequest(BaseModel):
    query: str
    top_k: int = 100


@app.post("/fetch_and_search")
async def fetch_and_search(request: FetchSearchRequest):
    try:
        current_run_path = scrape_reddit(scrapes_per_subreddit=100)
        
        # Check if vector search results already exist.
        output_filename = os.path.join(current_run_path, "vector_search_results.txt")
        if os.path.exists(output_filename):
            print("Vector search results already exist. Skipping vector database creation and search.")
            return {"message": "Search results already exist.", "output_filename": output_filename}
        else:
            create_vector_database(current_run_path, batch_size=95, index_name="MCP")
            output_filename = search_vector_db(index_name="MCP", query=request.query, current_run_path=current_run_path, top_k=request.top_k)
            return {"message": "Fetch and search completed successfully", "output_filename": output_filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 