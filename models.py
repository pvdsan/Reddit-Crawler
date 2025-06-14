# models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import os

# Enums for standardization
class AnalysisModel(str, Enum):
    GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"

class VectorModel(str, Enum):
    LLAMA_TEXT_EMBED_V2 = "llama-text-embed-v2"

# Input Models
class RedditScrapeRequest(BaseModel):
    scrapes_per_subreddit: int = Field(
        default=100, 
        ge=1, 
        le=1000,
        description="Number of posts to scrape per subreddit"
    )
    subreddits_file: Optional[str] = Field(
        default="subreddits.txt",
        description="Path to file containing subreddit list"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scrapes_per_subreddit": 100,
                "subreddits_file": "subreddits.txt"
            }
        }
    }

class VectorDatabaseRequest(BaseModel):
    run_path: str = Field(..., description="Path to the run directory containing scraped data")
    batch_size: int = Field(
        default=95, 
        ge=1, 
        le=200,
        description="Batch size for uploading vectors to Pinecone"
    )
    index_name: str = Field(
        default="tech-ideas-py",
        description="Name of the Pinecone index"
    )
    vector_model: VectorModel = Field(
        default=VectorModel.LLAMA_TEXT_EMBED_V2,
        description="Embedding model to use"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "run_path": "runs/2025-06-14_14_26",
                "batch_size": 95,
                "index_name": "tech-ideas-py",
                "vector_model": "llama-text-embed-v2"
            }
        }
    }

class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    index_name: str = Field(
        default="tech-ideas-py",
        description="Name of the Pinecone index to search"
    )
    run_path: str = Field(..., description="Path to save search results")
    top_k: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of top results to return"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "AI MCP server product ideas for hackathon",
                "index_name": "tech-ideas-py", 
                "run_path": "runs/2025-06-14_14_26",
                "top_k": 100
            }
        }
    }

class AIAnalysisRequest(BaseModel):
    query: str = Field(..., description="Analysis query/prompt")
    run_path: str = Field(..., description="Path containing vector search results")
    model: AnalysisModel = Field(
        default=AnalysisModel.GEMINI_2_0_FLASH,
        description="AI model to use for analysis"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Generate top 5 AI MCP server product ideas",
                "run_path": "runs/2025-06-14_14_26",
                "model": "gemini-2.0-flash-exp"
            }
        }
    }

class CustomQueryRequest(BaseModel):
    query_text: str = Field(..., description="Custom query text to save")
    query_file_path: str = Field(
        default="Ideation_Query.txt",
        description="Path to save the query file"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query_text": "What are the most innovative startup ideas in AI?",
                "query_file_path": "Custom_Query.txt"
            }
        }
    }

# Output Models
class RedditScrapeResult(BaseModel):
    success: bool = Field(..., description="Whether scraping was successful")
    run_path: str = Field(..., description="Path to the created run directory")
    total_posts_scraped: int = Field(..., description="Total number of posts collected")
    subreddits_processed: int = Field(..., description="Number of subreddits successfully processed")
    failed_subreddits: List[str] = Field(default=[], description="List of subreddits that failed")
    processing_time: float = Field(..., description="Time taken to scrape in seconds")
    data_file_path: str = Field(..., description="Path to the raw scraped data JSON file")
    file_size_mb: float = Field(..., description="Size of the scraped data file in MB")

class VectorDatabaseResult(BaseModel):
    success: bool = Field(..., description="Whether vector database creation was successful")
    index_name: str = Field(..., description="Name of the Pinecone index")
    total_records: int = Field(..., description="Total number of records processed")
    records_uploaded: int = Field(..., description="Number of records successfully uploaded")
    failed_records: int = Field(..., description="Number of records that failed to upload")
    processing_time: float = Field(..., description="Time taken to process vectors in seconds")
    rate_limit_hits: int = Field(default=0, description="Number of rate limit errors encountered")

class VectorSearchResult(BaseModel):
    success: bool = Field(..., description="Whether search was successful")
    query: str = Field(..., description="The search query used")
    results_count: int = Field(..., description="Number of results found")
    results_file_path: str = Field(..., description="Path to the search results file")
    file_size_kb: float = Field(..., description="Size of results file in KB")
    search_time: float = Field(..., description="Time taken to search in seconds")
    top_score: Optional[float] = Field(None, description="Highest similarity score")

class AIAnalysisResult(BaseModel):
    success: bool = Field(..., description="Whether AI analysis was successful")
    model_used: str = Field(..., description="AI model used for analysis")
    analysis_file_path: str = Field(..., description="Path to the generated analysis file")
    file_size_kb: float = Field(..., description="Size of analysis file in KB")
    processing_time: float = Field(..., description="Time taken for AI analysis in seconds")
    word_count: int = Field(..., description="Number of words in the generated analysis")

class PipelineStatus(BaseModel):
    run_path: Optional[str] = Field(None, description="Current active run path")
    steps_completed: List[str] = Field(default=[], description="Pipeline steps completed")
    current_step: Optional[str] = Field(None, description="Currently executing step")
    data_available: bool = Field(default=False, description="Whether scraped data is available")
    vector_db_ready: bool = Field(default=False, description="Whether vector database is ready")
    search_results_available: bool = Field(default=False, description="Whether search results exist")
    ai_analysis_complete: bool = Field(default=False, description="Whether AI analysis is complete")

class SystemHealth(BaseModel):
    status: str = Field(..., description="Overall system health status")
    reddit_api: bool = Field(..., description="Reddit API connection status")
    pinecone_api: bool = Field(..., description="Pinecone API connection status") 
    gemini_api: bool = Field(..., description="Gemini API connection status")
    config_loaded: bool = Field(..., description="Configuration loading status")
    runs_directory_accessible: bool = Field(..., description="Runs directory access status")
    last_successful_run: Optional[str] = Field(None, description="Last successful pipeline run")

class FileInfo(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    exists: bool = Field(..., description="Whether file exists")
    size_bytes: int = Field(..., description="File size in bytes")
    size_readable: str = Field(..., description="Human readable file size")
    modified_time: str = Field(..., description="Last modified timestamp")
    
class RunDirectoryInfo(BaseModel):
    run_path: str = Field(..., description="Path to the run directory")
    files: List[FileInfo] = Field(..., description="List of files in the run directory")
    total_size_mb: float = Field(..., description="Total size of all files in MB")
    creation_time: str = Field(..., description="Directory creation timestamp")

# Error Models
class PipelineError(BaseModel):
    error_code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error occurrence timestamp")
    step: Optional[str] = Field(None, description="Pipeline step where error occurred") 