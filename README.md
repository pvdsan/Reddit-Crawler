# LLM-Powered Reddit Search via MCP Server

This project provides a powerful MCP (Meta-Controller Protocol) server that enables Large Language Models (LLMs) and autonomous agents to search and analyze real-time conversations on Reddit. By exposing a simple, tool-callable API, this server allows LLMs to query what users are saying about specific topics, effectively giving them the ability to "browse" Reddit for information.

---

## Features

- **MCP-Enabled Tool for LLMs**: Designed for plug-and-play use by LLM agents, allowing them to perform Reddit searches as part of their reasoning process.
- **Real-Time Reddit Search**: Dynamically searches subreddits and scrapes conversations based on topics provided by the LLM.
- **Semantic Analysis Pipeline**: Includes a full backend pipeline for vectorization, semantic search, and AI-powered summarization of Reddit data.
- **Simple API Endpoint**: A single `/fetch_and_search` endpoint makes it easy for an agent to formulate a tool call.
- **Containerized & Deployable**: Ready to be deployed as a microservice with Docker and Docker Compose.

---

## How It Works: An LLM's Perspective

This server acts as a tool that an LLM can call when it needs information from Reddit. The process is seamless:

1.  **LLM Agent's Goal**: An LLM agent decides it needs to know what Reddit users are saying about a specific subject to answer a user's complex `query`.
2.  **Tool Call**: The agent intelligently simplifies the user's query into a concise `topic` (e.g., "backend development," "sci-fi books"). This `topic` is used as a search term to find relevant subreddits. It then makes a POST request to the `/fetch_and_search` endpoint, providing both the original `query` and the simplified `topic`.
3.  **MCP Server Processing**: The server receives the request and executes its pipeline:
    *   Uses the `topic` to find relevant subreddits.
    *   Scrapes posts and comments in real-time.
    *   Performs a vector search to find the most relevant information.
    *   Uses its own internal LLM (Gemini) to synthesize the findings.
4.  **Response to Agent**: The server returns a clean, summarized text answer directly to the LLM agent, which can then use this information in its final response to the user.

---

## Project Structure

```
Reddit-Crawler/
├── docker-compose.yml
├── Dockerfile
├── secrets.yaml             # API keys and secrets (user must create and fill)
├── requirements.txt
├── runs/                    # Output directories for each run
└── src/
    ├── create_vector_database.py
    ├── gemini_retrieval.py
    ├── ingestion_dynamic.py
    ├── search_vector_db.py
    ├── services.py          # FastAPI server
    └── utils.py
```

---

## Setup

### 1. Clone the Repository

```bash
git clone <repo-url>
cd Reddit-Crawler-MCP
```

### 2. Install Docker & Docker Compose

Ensure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

### 3. Configure API Keys

Create a file named `secrets.yaml` in the project root. This file is essential for the server to function.

```yaml
REDDIT_CLIENT_ID: "your_reddit_client_id"
REDDIT_CLIENT_SECRET: "your_reddit_client_secret"
REDDIT_USER_AGENT: "your_custom_user_agent"
REDDIT_USERNAME: "your_reddit_username"
REDDIT_PASSWORD: "your_reddit_password"
PINECONE_API_KEY: "your_pinecone_api_key"
GEMINI_API_KEY: "your_gemini_api_key"
```

**Never share your `secrets.yaml` or commit it to public repositories.**

---

## Usage

### 1. Start the Server

```bash
docker-compose up --build
```

The MCP server will start and be available at `http://localhost:8001`.

### 2. Example: LLM Agent Usage

This server is designed to be used as a tool by an LLM agent. Here's a conceptual example:

**Agent's Goal**: A user asks, "What are the most innovative server-side frameworks people are discussing on Reddit, especially regarding performance and scalability?"

**Agent's Internal Monologue (Thought Process)**:
1.  The user has a complex `query` about innovative server-side frameworks.
2.  To find the right communities, I need to simplify this into a `topic` for searching subreddits. A good `topic` would be "backend development" or "web dev". I'll use "backend development".
3.  I will call the Reddit search tool with the original `query` and my simplified `topic`.

**Agent's Tool Call (API Request)**:
The agent makes a POST request to `http://localhost:8001/fetch_and_search` with the following body:
```json
{
  "query": "What are the most innovative server-side frameworks people are discussing on Reddit, especially regarding performance and scalability?",
  "topic": "backend development"
}
```

**Server's Response (Returned to Agent)**:
The server processes the request and returns a concise summary for the agent to use:
```json
{
  "response": "Based on recent discussions in subreddits like r/backend, r/webdev, and r/programming, developers are highlighting Rust-based frameworks like Actix-web for top-tier performance. For scalability, many are still recommending established players like Django and Ruby on Rails, but also point to Elixir's Phoenix framework for its concurrency features..."
}
```

The agent can now incorporate this structured information into its final answer to the user.

### 3. Manual Testing with cURL

You can test the endpoint manually using `curl`:

```bash
curl -X POST "http://localhost:8001/fetch_and_search" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "Most innovative server-side frameworks for performance", "topic": "backend development"}'
```

---