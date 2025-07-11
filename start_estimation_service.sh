#!/bin/bash
# start_estimation_service.sh - Script to start the Software Effort Estimation Service

# Check if the virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the service
echo "Starting Software Effort Estimation Service..."
python -m requirement_analyzer.api

echo "Service is running at http://localhost:8000"
