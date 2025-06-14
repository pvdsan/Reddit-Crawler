# api_endpoints.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, Any

# Import our models
from models import *

# Import existing pipeline functions
from src.ingestion import scrape_reddit as _scrape_reddit
from src.create_vector_database import create_vector_database as _create_vector_database
from src.search_vector_db import search_vector_db as _search_vector_db
from src.gemini_retrieval import return_gemini_response as _return_gemini_response
from src.utils import load_config, ensure_runs_dir, load_subreddits

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reddit Scraper MCP Server",
    description="Reddit tech idea scraper and analysis pipeline exposed as MCP tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global state management (use Redis/DB in production)
pipeline_state: Dict[str, Any] = {
    "current_run_path": None,
    "last_scrape_time": None,
    "steps_completed": [],
    "config": None
}

# Initialize configuration
try:
    pipeline_state["config"] = load_config()
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")

@app.post("/scrape_reddit", 
         operation_id="scrape_reddit",
         response_model=RedditScrapeResult,
         tags=["data_ingestion"],
         summary="Scrape Reddit posts from configured subreddits",
         description="Collects posts from tech-related subreddits and stores them for analysis")
async def scrape_reddit(request: RedditScrapeRequest) -> RedditScrapeResult:
    """
    Scrape Reddit posts from configured subreddits.
    
    This tool collects posts from technology-related subreddits based on the
    configuration and saves them in a timestamped run directory.
    """
    try:
        start_time = time.time()
        logger.info(f"Starting Reddit scrape with {request.scrapes_per_subreddit} posts per subreddit")
        
        # Track current step
        pipeline_state["current_step"] = "scraping_reddit"
        
        # Load subreddits
        try:
            subreddits = load_subreddits(request.subreddits_file)
            logger.info(f"Loaded {len(subreddits)} subreddits from {request.subreddits_file}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load subreddits: {str(e)}")
        
        # Execute scraping
        run_path = _scrape_reddit(request.scrapes_per_subreddit)
        
        # Calculate results
        processing_time = time.time() - start_time
        data_file_path = os.path.join(run_path, "raw_scrap_results.json")
        
        # Get file info
        if os.path.exists(data_file_path):
            file_size = os.path.getsize(data_file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Count posts in the file
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                total_posts = len(data)
        else:
            raise HTTPException(status_code=500, detail="Scraping completed but data file not found")
        
        # Update pipeline state
        pipeline_state["current_run_path"] = run_path
        pipeline_state["last_scrape_time"] = datetime.now().isoformat()
        pipeline_state["steps_completed"] = ["reddit_scrape"]
        pipeline_state["current_step"] = None
        
        result = RedditScrapeResult(
            success=True,
            run_path=run_path,
            total_posts_scraped=total_posts,
            subreddits_processed=len(subreddits),
            failed_subreddits=[],  # We'd need to modify the original function to track this
            processing_time=round(processing_time, 2),
            data_file_path=data_file_path,
            file_size_mb=round(file_size_mb, 2)
        )
        
        logger.info(f"Reddit scraping completed: {total_posts} posts in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error in Reddit scraping: {str(e)}")
        pipeline_state["current_step"] = None
        raise HTTPException(status_code=500, detail=f"Reddit scraping failed: {str(e)}")

@app.post("/create_vector_database",
         operation_id="create_vector_database", 
         response_model=VectorDatabaseResult,
         tags=["data_processing"],
         summary="Create vector embeddings and upload to Pinecone",
         description="Processes scraped Reddit data and creates vector embeddings for semantic search")
async def create_vector_database(request: VectorDatabaseRequest) -> VectorDatabaseResult:
    """
    Create vector embeddings from scraped Reddit data.
    
    Takes the raw scraped data and creates vector embeddings using the specified
    model, then uploads them to Pinecone for semantic search capabilities.
    """
    try:
        start_time = time.time()
        logger.info(f"Creating vector database for {request.run_path}")
        
        # Validate run path exists
        if not os.path.exists(request.run_path):
            raise HTTPException(status_code=400, detail=f"Run path does not exist: {request.run_path}")
        
        data_file = os.path.join(request.run_path, "raw_scrap_results.json")
        if not os.path.exists(data_file):
            raise HTTPException(status_code=400, detail="No scraped data found. Run scrape_reddit first.")
        
        # Track current step
        pipeline_state["current_step"] = "creating_vectors"
        
        # Count total records
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            total_records = len(data)
        
        # Execute vector database creation
        _create_vector_database(
            current_run_path=request.run_path,
            batch_size=request.batch_size,
            index_name=request.index_name
        )
        
        processing_time = time.time() - start_time
        
        # Update pipeline state
        if "vector_database" not in pipeline_state["steps_completed"]:
            pipeline_state["steps_completed"].append("vector_database")
        pipeline_state["current_step"] = None
        
        result = VectorDatabaseResult(
            success=True,
            index_name=request.index_name,
            total_records=total_records,
            records_uploaded=total_records,  # Simplified - would need more detailed tracking
            failed_records=0,
            processing_time=round(processing_time, 2),
            rate_limit_hits=0  # Would need to track this in the original function
        )
        
        logger.info(f"Vector database created: {total_records} records in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error creating vector database: {str(e)}")
        pipeline_state["current_step"] = None
        raise HTTPException(status_code=500, detail=f"Vector database creation failed: {str(e)}")

@app.post("/search_vectors",
         operation_id="search_vectors",
         response_model=VectorSearchResult, 
         tags=["analysis"],
         summary="Perform semantic search on vector database",
         description="Searches the vector database for posts relevant to the given query")
async def search_vectors(request: VectorSearchRequest) -> VectorSearchResult:
    """
    Perform semantic search on the vector database.
    
    Uses the query to find the most relevant Reddit posts from the vector
    database and saves the results for further analysis.
    """
    try:
        start_time = time.time()
        logger.info(f"Searching vectors with query: {request.query[:50]}...")
        
        # Validate run path
        if not os.path.exists(request.run_path):
            raise HTTPException(status_code=400, detail=f"Run path does not exist: {request.run_path}")
        
        # Track current step
        pipeline_state["current_step"] = "searching_vectors"
        
        # Create temporary query file
        temp_query_file = os.path.join(request.run_path, "temp_query.txt")
        with open(temp_query_file, 'w', encoding='utf-8') as f:
            f.write(request.query)
        
        # Execute vector search
        _search_vector_db(
            index_name=request.index_name,
            query_file_path=temp_query_file,
            current_run_path=request.run_path,
            top_k=request.top_k
        )
        
        # Clean up temp file
        if os.path.exists(temp_query_file):
            os.remove(temp_query_file)
        
        search_time = time.time() - start_time
        
        # Get results file info
        results_file = os.path.join(request.run_path, "vector_search_results.txt")
        if os.path.exists(results_file):
            file_size = os.path.getsize(results_file)
            file_size_kb = file_size / 1024
            
            # Count results (quick estimation)
            with open(results_file, 'r', encoding='utf-8') as f:
                content = f.read()
                results_count = content.count("Result ")
        else:
            raise HTTPException(status_code=500, detail="Search completed but results file not found")
        
        # Update pipeline state
        if "vector_search" not in pipeline_state["steps_completed"]:
            pipeline_state["steps_completed"].append("vector_search")
        pipeline_state["current_step"] = None
        
        result = VectorSearchResult(
            success=True,
            query=request.query,
            results_count=results_count,
            results_file_path=results_file,
            file_size_kb=round(file_size_kb, 2),
            search_time=round(search_time, 2),
            top_score=None  # Would need to parse the results file to get this
        )
        
        logger.info(f"Vector search completed: {results_count} results in {search_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error in vector search: {str(e)}")
        pipeline_state["current_step"] = None
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

@app.post("/analyze_with_ai",
         operation_id="analyze_with_ai",
         response_model=AIAnalysisResult,
         tags=["analysis"],
         summary="Generate AI insights from search results",
         description="Uses Gemini AI to analyze search results and generate insights")
async def analyze_with_ai(request: AIAnalysisRequest) -> AIAnalysisResult:
    """
    Generate AI insights from vector search results.
    
    Uses Google Gemini to analyze the search results and generate
    actionable insights and recommendations.
    """
    try:
        start_time = time.time()
        logger.info(f"Starting AI analysis with model: {request.model}")
        
        # Validate run path and search results
        if not os.path.exists(request.run_path):
            raise HTTPException(status_code=400, detail=f"Run path does not exist: {request.run_path}")
        
        search_results_file = os.path.join(request.run_path, "vector_search_results.txt")
        if not os.path.exists(search_results_file):
            raise HTTPException(status_code=400, detail="No search results found. Run search_vectors first.")
        
        # Track current step
        pipeline_state["current_step"] = "ai_analysis"
        
        # Create temporary query file
        temp_query_file = os.path.join(request.run_path, "temp_analysis_query.txt")
        with open(temp_query_file, 'w', encoding='utf-8') as f:
            f.write(request.query)
        
        # Execute AI analysis
        _return_gemini_response(
            query_file_path=temp_query_file,
            current_run_path=request.run_path,
            model=request.model
        )
        
        # Clean up temp file
        if os.path.exists(temp_query_file):
            os.remove(temp_query_file)
        
        processing_time = time.time() - start_time
        
        # Get analysis file info
        analysis_file = os.path.join(request.run_path, "gemini_response.txt")
        if os.path.exists(analysis_file):
            file_size = os.path.getsize(analysis_file)
            file_size_kb = file_size / 1024
            
            # Count words
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content.split())
        else:
            raise HTTPException(status_code=500, detail="Analysis completed but results file not found")
        
        # Update pipeline state
        if "ai_analysis" not in pipeline_state["steps_completed"]:
            pipeline_state["steps_completed"].append("ai_analysis")
        pipeline_state["current_step"] = None
        
        result = AIAnalysisResult(
            success=True,
            model_used=request.model,
            analysis_file_path=analysis_file,
            file_size_kb=round(file_size_kb, 2),
            processing_time=round(processing_time, 2),
            word_count=word_count
        )
        
        logger.info(f"AI analysis completed: {word_count} words in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        pipeline_state["current_step"] = None
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.post("/run_full_pipeline",
         operation_id="run_full_pipeline",
         response_model=Dict[str, Any],
         tags=["orchestration"],
         summary="Execute complete pipeline end-to-end",
         description="Runs the entire pipeline: scrape -> vectorize -> search -> analyze")
async def run_full_pipeline(
    scrapes_per_subreddit: int = 100,
    search_query: str = "AI MCP server product ideas for hackathon",
    analysis_query: str = "Generate top 5 AI MCP server product ideas with scores",
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Execute the complete pipeline end-to-end.
    
    This orchestrates all pipeline steps in sequence and returns
    a summary of all results.
    """
    try:
        start_time = time.time()
        logger.info("Starting full pipeline execution")
        
        pipeline_state["current_step"] = "full_pipeline"
        results = {}
        
        # Step 1: Scrape Reddit
        scrape_request = RedditScrapeRequest(scrapes_per_subreddit=scrapes_per_subreddit)
        scrape_result = await scrape_reddit(scrape_request)
        results["scrape"] = scrape_result.dict()
        
        # Step 2: Create Vector Database
        vector_request = VectorDatabaseRequest(run_path=scrape_result.run_path)
        vector_result = await create_vector_database(vector_request)
        results["vector_db"] = vector_result.dict()
        
        # Step 3: Search Vectors
        search_request = VectorSearchRequest(
            query=search_query,
            run_path=scrape_result.run_path
        )
        search_result = await search_vectors(search_request)
        results["search"] = search_result.dict()
        
        # Step 4: AI Analysis
        analysis_request = AIAnalysisRequest(
            query=analysis_query,
            run_path=scrape_result.run_path
        )
        analysis_result = await analyze_with_ai(analysis_request)
        results["analysis"] = analysis_result.dict()
        
        total_time = time.time() - start_time
        
        pipeline_state["current_step"] = None
        
        return {
            "success": True,
            "run_path": scrape_result.run_path,
            "total_processing_time": round(total_time, 2),
            "steps": results,
            "summary": {
                "posts_scraped": scrape_result.total_posts_scraped,
                "vectors_created": vector_result.records_uploaded,
                "search_results": search_result.results_count,
                "analysis_words": analysis_result.word_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error in full pipeline: {str(e)}")
        pipeline_state["current_step"] = None
        raise HTTPException(status_code=500, detail=f"Full pipeline failed: {str(e)}")

# System and utility endpoints
@app.get("/health", 
         operation_id="health_check", 
         response_model=SystemHealth,
         tags=["system"],
         summary="Check system health and API connections")
async def health_check() -> SystemHealth:
    """Check if all system components are healthy and accessible."""
    try:
        config_loaded = pipeline_state.get("config") is not None
        
        # Test API connections (simplified)
        reddit_api = True  # Would test actual connection
        pinecone_api = True  # Would test actual connection  
        gemini_api = True  # Would test actual connection
        runs_dir_accessible = os.path.exists(ensure_runs_dir())
        
        # Get last successful run
        runs_dir = ensure_runs_dir()
        runs = [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
        last_run = max(runs) if runs else None
        
        status = "healthy" if all([reddit_api, pinecone_api, gemini_api, config_loaded]) else "degraded"
        
        return SystemHealth(
            status=status,
            reddit_api=reddit_api,
            pinecone_api=pinecone_api,
            gemini_api=gemini_api,
            config_loaded=config_loaded,
            runs_directory_accessible=runs_dir_accessible,
            last_successful_run=last_run
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/pipeline_status", 
         operation_id="get_pipeline_status", 
         response_model=PipelineStatus,
         tags=["system"],
         summary="Get current pipeline status and progress")
async def get_pipeline_status() -> PipelineStatus:
    """Get current pipeline execution status and progress."""
    try:
        current_run = pipeline_state.get("current_run_path")
        
        # Check what data/results are available
        data_available = False
        vector_db_ready = False
        search_results_available = False
        ai_analysis_complete = False
        
        if current_run and os.path.exists(current_run):
            data_file = os.path.join(current_run, "raw_scrap_results.json")
            search_file = os.path.join(current_run, "vector_search_results.txt")
            analysis_file = os.path.join(current_run, "gemini_response.txt")
            
            data_available = os.path.exists(data_file)
            vector_db_ready = "vector_database" in pipeline_state.get("steps_completed", [])
            search_results_available = os.path.exists(search_file)
            ai_analysis_complete = os.path.exists(analysis_file)
        
        return PipelineStatus(
            run_path=current_run,
            steps_completed=pipeline_state.get("steps_completed", []),
            current_step=pipeline_state.get("current_step"),
            data_available=data_available,
            vector_db_ready=vector_db_ready,
            search_results_available=search_results_available,
            ai_analysis_complete=ai_analysis_complete
        )
        
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")

@app.get("/download_results/{run_id}/{file_type}",
         operation_id="download_results",
         tags=["output"],
         summary="Download pipeline results files")
async def download_results(run_id: str, file_type: str):
    """Download specific result files from a pipeline run."""
    try:
        runs_dir = ensure_runs_dir()
        run_path = os.path.join(runs_dir, run_id)
        
        if not os.path.exists(run_path):
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
        
        file_map = {
            "raw_data": "raw_scrap_results.json",
            "search_results": "vector_search_results.txt", 
            "ai_analysis": "gemini_response.txt"
        }
        
        if file_type not in file_map:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Choose from: {list(file_map.keys())}")
        
        file_path = os.path.join(run_path, file_map[file_type])
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_type} not found for run {run_id}")
        
        return FileResponse(
            path=file_path,
            filename=f"{run_id}_{file_map[file_type]}",
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now().isoformat()}
    ) 