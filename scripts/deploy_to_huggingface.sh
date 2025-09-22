#!/bin/bash

# Script to package and deploy the project to Hugging Face

echo "=== Packaging for Hugging Face Deployment ==="

# Create a temporary directory for the package
PACKAGE_DIR="huggingface_package"
mkdir -p $PACKAGE_DIR

# Copy essential files
echo "Copying essential files..."
cp app.py $PACKAGE_DIR/
cp Dockerfile $PACKAGE_DIR/
cp packages.py $PACKAGE_DIR/
cp -r templates $PACKAGE_DIR/
cp requirements.txt $PACKAGE_DIR/
cp README_HUGGINGFACE.md $PACKAGE_DIR/README.md

# Copy model-related files
echo "Copying model files..."
mkdir -p $PACKAGE_DIR/models
cp -r models/* $PACKAGE_DIR/models/ 2>/dev/null || echo "No model files to copy"

# Copy API modules
echo "Copying API modules..."
cp feedback_api.py $PACKAGE_DIR/
cp feedback_collector.py $PACKAGE_DIR/
cp feedback_feature_extractor.py $PACKAGE_DIR/
cp model_retrainer.py $PACKAGE_DIR/
cp cocomo_ii_predictor.py $PACKAGE_DIR/

# Copy requirement analyzer module
echo "Copying requirement analyzer module..."
mkdir -p $PACKAGE_DIR/requirement_analyzer
cp -r requirement_analyzer/* $PACKAGE_DIR/requirement_analyzer/

# Create datasets directory
echo "Creating datasets structure..."
mkdir -p $PACKAGE_DIR/datasets/feedback

# Create an empty feedback data file if it doesn't exist
if [ ! -f "datasets/feedback/feedback_data.csv" ]; then
    mkdir -p datasets/feedback
    echo "project_id,task_id,requirement_text,estimated_effort,actual_effort,effort_unit,model_used,features,timestamp" > datasets/feedback/feedback_data.csv
fi

# Copy feedback data
cp -r datasets/feedback $PACKAGE_DIR/datasets/

# Create zip file
echo "Creating zip archive..."
zip -r huggingface_package.zip $PACKAGE_DIR

echo "===== Package created: huggingface_package.zip ====="
echo ""
echo "Instructions to upload to Hugging Face:"
echo "1. Go to https://huggingface.co/spaces"
echo "2. Click on 'Create new Space'"
echo "3. Choose 'Docker' as the Space SDK"
echo "4. Upload the huggingface_package.zip file and extract its contents"
echo "5. Commit the changes to deploy your app"
echo ""
echo "Your app will be available at https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME"
