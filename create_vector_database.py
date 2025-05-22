from pinecone import Pinecone
import time
import json
import random
import itertools
# from langchain_google_genai import GoogleGenerativeAIEmbeddings # This was unused, can be removed if not needed

def chunks(iterable, batch_size=200):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

# Initialize a Pinecone client with your API key
pc = Pinecone(api_key="pcsk_oE8i9_BuQ2tgsxyNxRwUKPcFvW34VuQ98SmJE88qtybKBA1R4uWVvExwiDryEgu3Bygzb")

# Load the preprocessed records
try:
    with open("pinecone_records.json", 'r') as f:
        records_to_upsert = json.load(f)
except FileNotFoundError:
    print("Error: 'pinecone_records.json' not found. Please run the preprocessing script first.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode JSON from 'pinecone_records.json'. Make sure it's valid.")
    exit()

if not records_to_upsert:
    print("No records found in 'pinecone_records.json'. Nothing to upsert.")
    exit()

# Create a dense index with integrated embedding (or connect if exists)
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

# Upsert the records into a namespace
print(f"Upserting {len(records_to_upsert)} records into namespace 'example-namespace' in batches...")

# Define batch size, matching your chunks function or Pinecone limits (e.g., 100-200 for upsert_records)
BATCH_SIZE = 95 # You can adjust this based on performance and Pinecone recommendations
total_upserted_count = 0

for record_chunk in chunks(records_to_upsert, batch_size=BATCH_SIZE):
    try:
        print(f"Upserting batch of {len(record_chunk)} records...")
        dense_index.upsert_records(namespace="example-namespace", records=list(record_chunk))
        total_upserted_count += len(record_chunk)
        print(f"Successfully upserted batch. Total upserted so far: {total_upserted_count}")
    except Exception as e:
        print(f"Error upserting batch: {e}")
        # Optionally, add more sophisticated error handling here, like retries or logging failed batches

print(f"Successfully upserted {total_upserted_count} records in total to namespace 'example-namespace'.")

# Optional: Describe index stats after upsert
# time.sleep(5) # Wait a bit for stats to update
# stats = dense_index.describe_index_stats()
# print("Index stats after upsert:")
# print(stats)