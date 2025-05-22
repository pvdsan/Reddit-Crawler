from pinecone import Pinecone
import time
import json
import random
import itertools


pc = Pinecone(api_key="pcsk_oE8i9_BuQ2tgsxyNxRwUKPcFvW34VuQ98SmJE88qtybKBA1R4uWVvExwiDryEgu3Bygzb")

index_name = "quickstart-py" # Ensure this matches the index used in pinecone_test.py if querying there
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

query = "What are some AI related startip ideas or issues that people face ?Are there any products people would like to buy"

reranked_results = dense_index.search(
    namespace="example-namespace",
    query={
        "top_k": 10,
        "inputs": {
            'text': query
        }
    },
    rerank={
        "model": "bge-reranker-v2-m3",
        "top_n": 10,
        "rank_fields": ["chunk_text"]
    }   
)

# Print the reranked results
for hit in reranked_results['result']['hits']:
    print(f"id: {hit['_id']}, score: {round(hit['_score'], 2)}, text: {hit['fields']['chunk_text']}")
    
    