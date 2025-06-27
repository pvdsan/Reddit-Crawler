from pinecone import Pinecone
import time
import json
import random
import itertools
import os
import yaml
from dotenv import load_dotenv

with open("secrets.yaml", 'r') as stream:
    keys = yaml.safe_load(stream)
    

def chunks(iterable, batch_size=200):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


def create_vector_database(current_run_path: str, batch_size: int = 95, index_name: str = "tech-ideas-py", namespace: str = "example-namespace"):
# Initialize a Pinecone client with your API key
    pc = Pinecone(api_key=keys['PINECONE_API_KEY'])
    
    raw_scraps_filename = os.path.join(current_run_path, "raw_scrap_results.json")

    # Load the preprocessed records
    try:
        with open(raw_scraps_filename, 'r', encoding="utf-8") as f:
            records_to_upsert = json.load(f)
    except FileNotFoundError:
        print(f"Error: '{raw_scraps_filename}' not found. Please run the preprocessing script first.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{raw_scraps_filename}'. Make sure it's valid.")
        return

    if not records_to_upsert:
        print(f"No records found in '{raw_scraps_filename}'. Nothing to upsert.")
        return

    # Create a dense index with integrated embedding (or connect if exists)
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

    # Upsert the records into a namespace
    print(f"Upserting {len(records_to_upsert)} records into namespace {index_name} in batches...")

    # Define batch size, matching your chunks function or Pinecone limits (e.g., 100-200 for upsert_records)
    total_upserted_count = 0

    for record_chunk in chunks(records_to_upsert, batch_size=batch_size):
        try:
            print(f"Upserting batch of {len(record_chunk)} records...")
            dense_index.upsert_records(namespace="example-namespace", records=list(record_chunk))
            total_upserted_count += len(record_chunk)
            print(f"Successfully upserted batch. Total upserted so far: {total_upserted_count}")
        except Exception as e:
            print(f"Error upserting batch: {e}")
            # Optionally, add more sophisticated error handling here, like retries or logging failed batches

    print(f"Successfully upserted {total_upserted_count} records in total to namespace 'example-namespace'.")

