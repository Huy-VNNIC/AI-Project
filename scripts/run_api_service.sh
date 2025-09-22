#!/bin/bash
# Simple script to run only the requirement analyzer API service

# Activate the virtual environment
source venv/bin/activate

# Run the FastAPI service
echo "Starting requirement analyzer API service..."
python -m requirement_analyzer.api

# Note: Press Ctrl+C to stop the service
