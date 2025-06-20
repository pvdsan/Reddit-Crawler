from pinecone import Pinecone
import time
import json
import random
import itertools
import os
from src.utils import load_config

# Load configuration
config = load_config("key.yaml")
if not config:
    raise ValueError("Could not load configuration from key.yaml")

pinecone_api_key = config.get("keys", {}).get("PINECONE")
if not pinecone_api_key:
    raise ValueError("PINECONE API key not found in configuration")

pc = Pinecone(api_key=pinecone_api_key)

def search_vector_db(index_name: str, query_file_path: str, current_run_path: str, top_k: int = 100):

    if not pc.has_index(index_name):
        print(f"Creating index '{index_name}' with integrated embeddings for 'llama-text-embed-v2'...")
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model":"llama-text-embed-v2",
                "field_map":{"text": "chunk_text"} # Pinecone will look for 'chunk_text' in your records
            }
        )
        print(f"Index '{index_name}' created. It might take a moment to be ready.")
        time.sleep(10) # Give a moment for the index to initialize
    else:
        print(f"Index '{index_name}' already exists. Connecting to it.")

    dense_index = pc.Index(index_name)

    #Load the query from the query file with UTF-8 encoding
    with open(query_file_path, "r", encoding="utf-8") as file:
        query = file.read()

    reranked_results = dense_index.search(
        namespace="example-namespace",
        query={
            "top_k": top_k,
            "inputs": {
                'text': query
            }
        },
        fields = ["chunk_text"]   
    )

    output_filename = os.path.join(current_run_path, f"vector_search_results.txt")
    with open(output_filename, 'w', encoding='utf-8') as f_out:
        print(f"Saving vector search results to {output_filename}...")
        if reranked_results and 'result' in reranked_results and 'hits' in reranked_results['result']:
            for i, hit in enumerate(reranked_results['result']['hits']):
                hit_id = hit.get('_id', 'N/A')
                score = round(hit.get('_score', 0.0), 4) # Using .get for safety and rounding score
                text = hit.get('fields', {}).get('chunk_text', 'N/A')
            
                # Write to file
                f_out.write(f"Result {i+1}:\n")
                f_out.write(f"  ID: {hit_id}\n")
                f_out.write(f"  Score: {score}\n")
                f_out.write(f"  Text: {text}\n")
                f_out.write("--------------------------------------------------\n\n")
            print(f"Successfully saved {len(reranked_results['result']['hits'])} results to {output_filename}")
        else:
            message = "No results found to save."
            print(message)
            f_out.write(message + "\n")
    
    