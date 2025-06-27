from fastapi import FastAPI, HTTPException
# from fastapi.concurrency import run_in_threadpool
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import os
import uvicorn
from datetime import datetime
from .ingestion_static import scrape_reddit_static
from .ingestion_dynamic import scrape_reddit_dynamic
from .create_vector_database import create_vector_database
from .search_vector_db import search_vector_db
from .gemini_retrieval import return_gemini_response
app = FastAPI()

mcp = FastApiMCP(app)
# Mount the MCP server directly to your FastAPI app
mcp.mount()

class FetchSearchRequest(BaseModel):
    
    query: str  # The analysis/request that user wants to make 
    topic: str # The topic which shall be used to scrap subreddits from. Also used to name the index in Pinecone
    subreddit_limit: int = 2
    post_limit: int = 100
    top_k: int = 50
    




@app.post("/fetch_and_search")
async def fetch_and_search(request: FetchSearchRequest):
    try:
        # Construct the expected path for today's run
        date_str = datetime.now().strftime("%m_%d")
        run_name = f"{request.topic.lower().replace(' ', '')}_{date_str}"
        current_run_path = os.path.join("runs", run_name)

        # If a response from today already exists, return it
        if os.path.exists(current_run_path):
            if os.path.exists(os.path.join(current_run_path, "gemini_response.txt")):
                return {"response": open(os.path.join(current_run_path, "gemini_response.txt")).read()}
            search_vector_db(index_name=request.topic.lower().replace(' ', ''), query=request.query, current_run_path=current_run_path, top_k=request.top_k)
            gemini_response_text = return_gemini_response(query=request.query, current_run_path=current_run_path, model="gemini-2.5-flash-preview-05-20")
            return {"response": gemini_response_text}

        # Otherwise, run the full pipeline
        current_run_path = scrape_reddit_dynamic(topic=request.topic, subreddit_limit=request.subreddit_limit, post_limit=request.post_limit)
        
        create_vector_database(current_run_path, batch_size=95, index_name=request.topic.lower().replace(' ', ''))
        search_vector_db(index_name=request.topic.lower().replace(' ', ''), query=request.query, current_run_path=current_run_path, top_k=request.top_k)
        gemini_response_text = return_gemini_response(query=request.query, current_run_path=current_run_path, model="gemini-2.5-flash-preview-05-20")
        
        return {"response": gemini_response_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 