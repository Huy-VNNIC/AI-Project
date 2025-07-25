#!/bin/bash
# Script to retrain models with current feature set

# Activate virtual environment
source venv/bin/activate

echo "Retraining models with current feature set..."
python -m requirement_analyzer.retrain_models

echo "Retraining completed. Run the API with updated models."
