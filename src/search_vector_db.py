from pinecone import Pinecone
import time
import json
import random
import itertools
import os
import yaml

with open("secrets.yaml", 'r') as stream:
    keys = yaml.safe_load(stream)

pc = Pinecone(api_key=keys['PINECONE_API_KEY'])

def search_vector_db(index_name: str, query: str, current_run_path: str, top_k: int = 100, namespace: str = "example-namespace"):

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
    