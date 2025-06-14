# mcp_server.py
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from api_endpoints import app
import uvicorn
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP configuration
mcp = FastApiMCP(
    app,
    name="Reddit Scraper MCP Server",
    description="Advanced Reddit tech idea scraper and analysis pipeline exposed as MCP tools for LLM agents. Scrapes tech subreddits, creates vector embeddings, performs semantic search, and generates AI insights.",
    
    # Control which endpoints become MCP tools
    include_operations=[
        "scrape_reddit",           # Core data collection
        "create_vector_database",  # Vector embedding creation
        "search_vectors",          # Semantic search
        "analyze_with_ai",         # AI insights generation
        "run_full_pipeline",       # Complete workflow orchestration
        "health_check",            # System health monitoring
        "get_pipeline_status",     # Pipeline progress tracking
        "download_results"         # Results file access
    ]
)

# Mount MCP server to expose tools
mcp.mount()

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware for request logging
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Reddit Scraper MCP Server starting up...")
    logger.info("📊 MCP Tools available at: http://localhost:8001/mcp")
    logger.info("📖 API Documentation: http://localhost:8001/docs")
    logger.info("🔍 Alternative docs: http://localhost:8001/redoc")
    
    # Print available MCP tools
    logger.info("\n🛠️  Available MCP Tools:")
    tools = [
        "scrape_reddit - Collect posts from tech subreddits",
        "create_vector_database - Generate vector embeddings for semantic search", 
        "search_vectors - Find relevant posts using semantic search",
        "analyze_with_ai - Generate AI insights with Gemini",
        "run_full_pipeline - Execute complete workflow end-to-end",
        "health_check - Monitor system health and API connections",
        "get_pipeline_status - Track pipeline progress and state",
        "download_results - Access generated files and results"
    ]
    for tool in tools:
        logger.info(f"   • {tool}")
    
    logger.info("\n🎯 Ready for LLM agent interactions!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Reddit Scraper MCP Server shutting down...")

# Configuration class for easy customization
class ServerConfig:
    HOST = "0.0.0.0"
    PORT = 8001
    RELOAD = True
    LOG_LEVEL = "info"

def run_server():
    """Run the MCP server with the specified configuration"""
    config = ServerConfig()
    
    print(f"""
╭─────────────────────────────────────────────╮
│           Reddit Scraper MCP Server         │
├─────────────────────────────────────────────┤
│  🌐 Server: http://{config.HOST}:{config.PORT}              │
│  📊 MCP Tools: http://localhost:{config.PORT}/mcp      │
│  📖 Docs: http://localhost:{config.PORT}/docs          │
│  🔍 ReDoc: http://localhost:{config.PORT}/redoc        │
├─────────────────────────────────────────────┤
│  Available Tools:                           │
│  • scrape_reddit                           │
│  • create_vector_database                  │
│  • search_vectors                          │
│  • analyze_with_ai                         │
│  • run_full_pipeline                       │
│  • health_check                            │
│  • get_pipeline_status                     │
│  • download_results                        │
╰─────────────────────────────────────────────╯
    """)
    
    uvicorn.run(
        "mcp_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL,
        access_log=True
    )

if __name__ == "__main__":
    run_server() 