from google import genai
import os
from src.utils import load_config

# Load configuration
config = load_config("key.yaml")
if not config:
    raise ValueError("Could not load configuration from key.yaml")

def return_gemini_response(query_file_path: str, current_run_path: str, model: str = "gemini-2.0-flash-exp"):
    
    gemini_api_key = config.get("keys", {}).get("GEMINI")
    if not gemini_api_key:
        raise ValueError("GEMINI API key not found in configuration")
    
    client = genai.Client(api_key=gemini_api_key)

    with open(query_file_path, "r", encoding="utf-8") as file:
        query = file.read()
        
    filtered_posts = client.files.upload(file = os.path.join(current_run_path, f"vector_search_results.txt"))

    response = client.models.generate_content(
        model=model,
        contents=[query, filtered_posts]
    )

    with open(os.path.join(current_run_path, f"gemini_response.txt"), "w", encoding="utf-8") as file:
        file.write(response.text)
    
    
