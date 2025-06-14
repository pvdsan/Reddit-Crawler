# Reddit Tech Ideas Crawler

A sophisticated system designed to crawl, analyze, and retrieve technology-related ideas from Reddit using AI-powered analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (✅ Already installed)
- Reddit API credentials
- Google Gemini API key  
- Pinecone API key

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
✅ **Already completed!**

### 2. Configure API Keys

You need to set up three API services:

#### **Reddit API Setup**
1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your `client_id` and `client_secret`

#### **Google Gemini API Setup**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

#### **Pinecone API Setup**
1. Go to [Pinecone](https://www.pinecone.io/) and create an account
2. Create a new project
3. Get your API key from the dashboard

### 3. Update Configuration

Edit the `key.yaml` file with your API keys:

```yaml
keys: 
  GEMINI: your_gemini_api_key_here
  PINECONE: your_pinecone_api_key_here

reddit:
  client_id: your_reddit_client_id_here
  client_secret: your_reddit_client_secret_here
  username: your_reddit_username_here
  password: your_reddit_password_here
```

### 4. Run the Application

```bash
cd src
python main.py
```

## 📁 Project Structure

```
Reddit-Crawler/
├── src/
│   ├── main.py                 # Main execution script
│   ├── ingestion.py           # Reddit data collection
│   ├── create_vector_database.py  # Vector DB creation
│   ├── search_vector_db.py    # Vector search implementation
│   ├── gemini_retrieval.py    # AI analysis integration
│   └── utils.py              # Utility functions
├── runs/                      # Directory for run outputs (auto-created)
├── subreddits.txt            # List of target subreddits
├── Ideation_Query.txt        # Search queries
├── requirements.txt          # Project dependencies
├── key.yaml                 # Configuration file
└── README.md               # This file
```

## 🔧 How It Works

1. **Data Collection**: Scrapes posts from subreddits listed in `subreddits.txt`
2. **Vector Database**: Creates embeddings and stores them in Pinecone
3. **Semantic Search**: Searches for relevant posts based on queries in `Ideation_Query.txt`
4. **AI Analysis**: Uses Gemini AI to analyze results and generate insights

## 📝 Configuration Files

- **`subreddits.txt`**: List of subreddits to scrape (one per line)
- **`Ideation_Query.txt`**: Search queries for finding relevant content
- **`key.yaml`**: API keys and configuration

## 📊 Output

Results are stored in timestamped directories under `runs/`:
- `raw_scrap_results.json`: Raw scraped Reddit data
- `vector_search_results.txt`: Semantic search results
- `gemini_response.txt`: AI-generated insights

## ⚡ Current Status

✅ Dependencies installed  
✅ Code fixed for your system  
⚠️  **Next Step**: Configure API keys in `key.yaml`  

## 🔑 Security Note

The current `key.yaml` file contains example/demo keys. **Replace them with your own API keys** before running the application.

## 🐛 Troubleshooting

- **Import errors**: Make sure you're running from the project root directory
- **API errors**: Verify your API keys are correct and have proper permissions
- **Reddit rate limits**: The script includes built-in rate limiting, but heavy usage may still hit limits

## 📞 Need Help?

If you encounter any issues, check the error messages - they'll guide you to the specific configuration that needs attention. 