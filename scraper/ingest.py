import json
import os
import sys
import glob
import requests
import argparse

BACKEND_URL = os.environ.get("BACKEND_INGEST_URL", "http://localhost:3000/api/v1/import_prices")

def ingest_file(filepath):
    print(f"Starting ingestion for {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    print(f"Loaded batch for pharmacy: {data.get('pharmacy_name', 'Unknown')}")
    print(f"Items count: {data.get('items_count', 0)}")

    try:
        print(f"Sending payload to {BACKEND_URL}...")
        response = requests.post(
            BACKEND_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in (200, 201):
            print(f"Success! Backend responded with status {response.status_code}.")
            return True
        else:
            print(f"Failed! Backend responded with status {response.status_code}.")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"ConnectionError: Could not connect to {BACKEND_URL}.")
        print("Note: If the backend is not running yet, this is expected.")
        return False
    except Exception as e:
        print(f"Error during request: {e}")
        return False

def main(files):
    if not files:
        # Auto-discover if no files provided
        files = glob.glob("*_products.json")

    if not files:
        print("No *_products.json files found to ingest.")
        sys.exit(0)

    print(f"Found {len(files)} files to ingest.")
    success_count = 0

    for f in files:
        if ingest_file(f):
            success_count += 1
            # Optionally archive or remove the file after successful ingestion
            # os.rename(f, f"archive_{f}")
        print("-" * 40)

    print(f"Ingestion process completed. Successfully ingested {success_count}/{len(files)} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest scraped JSON batches to the backend.")
    parser.add_argument("files", nargs="*", help="Optional list of JSON files to ingest. If omitted, discovers *_products.json")
    args = parser.parse_args()

    main(args.files)
