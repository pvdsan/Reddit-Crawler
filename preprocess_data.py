import json

def transform_data(input_filepath="results2.json", output_filepath="pinecone_records.json"):
    """
    Loads data from the input JSON file, transforms it into the desired format
    for Pinecone, and saves it to the output JSON file.
    
    Each record in the output will have:
    - "_id": from the "id" field of the input.
    - "chunk_text": a combination of "title" and "body" fields from the input.
    """
    transformed_records = []
    skipped_items_count = 0

    try:
        with open(input_filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_filepath}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_filepath}'. Make sure it's a valid JSON file.")
        return

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and 'id' in item and 'title' in item and 'body' in item:
                record = {
                    "_id": str(item.get("id")),  # Ensure ID is a string
                    "chunk_text": f"{item.get('title', '')} {item.get('body', '')}".strip()
                    # You can add other metadata fields here if they exist in your source
                    # and you want them in the Pinecone records.
                    # For example: "category": item.get("category", "default_category")
                }
                transformed_records.append(record)
            else:
                skipped_items_count += 1
                print(f"Warning: Skipping item due to missing 'id', 'title', or 'body', or incorrect format: {item}")
    elif isinstance(data, dict):
        # This handles the case where results2.json might be a single JSON object
        # or a dictionary with a key containing the list of items.
        # If it's a single item:
        if 'id' in data and 'title' in data and 'body' in data:
            record = {
                "_id": str(data.get("id")),
                "chunk_text": f"{data.get('title', '')} {data.get('body', '')}".strip()
            }
            transformed_records.append(record)
        else:
            # If you expect the list to be under a specific key in a root dictionary,
            # you would add logic here, e.g.:
            # if 'entries' in data and isinstance(data['entries'], list):
            #    for item in data['entries']:
            #        # ... (transformation logic as above) ...
            # else:
            #    skipped_items_count +=1 # or count the whole dict as one skipped item
            print(f"Warning: Input data from '{input_filepath}' is a dictionary but does not have the expected 'id', 'title', and 'body' keys directly. If your records are nested, please adjust the script.")
            skipped_items_count += 1 # Assuming the whole dict is one item that can't be processed
    else:
        print(f"Error: Data in '{input_filepath}' is not a list or a recognizable dictionary format. Found type: {type(data)}")
        return

    try:
        with open(output_filepath, 'w') as f:
            json.dump(transformed_records, f, indent=4)
        print(f"Successfully transformed {len(transformed_records)} records.")
        if skipped_items_count > 0:
            print(f"Skipped {skipped_items_count} items due to missing fields or format issues.")
        print(f"Transformed data saved to '{output_filepath}'")
    except IOError:
        print(f"Error: Could not write to output file '{output_filepath}'.")

if __name__ == "__main__":
    transform_data() 