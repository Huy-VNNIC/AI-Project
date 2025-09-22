#!/bin/bash
# Script to set up the requirements analyzer and effort estimation service

# Set up Python environment
echo "Setting up Python environment..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Download necessary resources
echo "Downloading necessary resources..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
python -m spacy download en_core_web_sm

# Create models directory if it doesn't exist
mkdir -p models

# Train requirement classifier models
echo "Training requirement classifier models..."
python requirement_analyzer/train_models.py --skip-effort-models

# Print success message
echo "Setup completed successfully!"
echo "To start the estimation service, run: ./run_estimation_service.sh"
