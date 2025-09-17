#!/bin/bash

# Script to package the project for Hugging Face

echo "Creating package for Hugging Face deployment..."

# Create a temporary directory for the package
PACKAGE_DIR="huggingface_package"
mkdir -p $PACKAGE_DIR

# Copy essential files
cp app.py $PACKAGE_DIR/
cp -r templates $PACKAGE_DIR/
cp Spacefile $PACKAGE_DIR/
cp requirements.txt $PACKAGE_DIR/
cp README_HUGGINGFACE.md $PACKAGE_DIR/README.md

# Copy model files
mkdir -p $PACKAGE_DIR/models
cp -r models/* $PACKAGE_DIR/models/ 2>/dev/null || echo "No model files to copy"

# Copy essential Python modules
cp feedback_api.py $PACKAGE_DIR/
cp feedback_collector.py $PACKAGE_DIR/
cp feedback_feature_extractor.py $PACKAGE_DIR/
cp model_retrainer.py $PACKAGE_DIR/
cp cocomo_ii_predictor.py $PACKAGE_DIR/

# Create datasets directory
mkdir -p $PACKAGE_DIR/datasets/feedback

# Create an empty feedback data file if it doesn't exist
if [ ! -f "datasets/feedback/feedback_data.csv" ]; then
    mkdir -p datasets/feedback
    echo "project_id,task_id,requirement_text,estimated_effort,actual_effort,effort_unit,model_used,features,timestamp" > datasets/feedback/feedback_data.csv
fi

# Copy feedback data
cp -r datasets/feedback $PACKAGE_DIR/datasets/

# Create a zip file
zip -r huggingface_package.zip $PACKAGE_DIR

echo "Package created: huggingface_package.zip"
echo "You can now upload this package to Hugging Face Spaces"
