#!/bin/bash

# Pipeline Script to run all scrapers and ingest data

# Change to the directory where the script is located
cd "$(dirname "$0")"

echo "========================================"
echo "Starting Scraping and Ingestion Pipeline"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment (venv) not found in the scraper directory."
    echo "Please set up the environment first."
else
    # Activate virtual environment
    source venv/Scripts/Activate

    # Execute all scraper scripts
    # Currently, we have cruz_verde.py. We'll find all python scripts except ingest.py, schema.py and test scripts.
    SCRAPERS=$(find . -maxdepth 1 -name "*.py" -not -name "ingest.py" -not -name "schema.py" -not -name "test_*" -not -name "__*")

    if [ -z "$SCRAPERS" ]; then
        echo "No scraper scripts found."
    else
        for scraper in $SCRAPERS; do
            echo "----------------------------------------"
            echo "Running scraper: $scraper"
            python3 "$scraper"
            if [ $? -ne 0 ]; then
                echo "Warning: Scraper $scraper encountered an error."
            fi
        done
    fi

    echo "----------------------------------------"
    echo "Running Data Ingestion..."
    # Execute the ingestion script
    python3 ingest.py

    echo "========================================"
    echo "Pipeline Execution Completed."
    echo "========================================"

    # Deactivate virtual environment
    deactivate
fi
