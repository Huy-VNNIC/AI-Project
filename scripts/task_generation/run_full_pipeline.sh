#!/bin/bash

# Full pipeline script for task generation system
# Runs all steps from data processing to model training

set -e  # Exit on error

echo "================================================================================"
echo "🚀 TASK GENERATION - FULL TRAINING PIPELINE"
echo "================================================================================"

# Check if we're in the right directory
if [ ! -d "requirement_analyzer/dataset_large_1m" ] && [ ! -d "requirement_analyzer/dataset_small_10k" ]; then
    echo "❌ Error: Dataset not found!"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Determine which dataset to use
if [ -d "requirement_analyzer/dataset_large_1m" ]; then
    DATASET="requirement_analyzer/dataset_large_1m"
    echo "📊 Using LARGE dataset (1M rows)"
elif [ -d "requirement_analyzer/dataset_small_10k" ]; then
    DATASET="requirement_analyzer/dataset_small_10k"
    echo "📊 Using SMALL dataset (10K rows)"
else
    echo "❌ No dataset found!"
    exit 1
fi

# Create output directories
mkdir -p data/processed
mkdir -p data/splits
mkdir -p models/task_gen
mkdir -p report

echo ""
echo "================================================================================"
echo "Step 1/6: Dataset Scanning & Quality Report"
echo "================================================================================"
python scripts/task_generation/01_scan_dataset.py \
    --dataset "$DATASET" \
    --output report/data_quality_report

echo ""
echo "================================================================================"
echo "Step 2/6: Data Cleaning & Parquet Conversion"
echo "================================================================================"
python scripts/task_generation/02_build_parquet.py \
    --input "$DATASET" \
    --output data/processed \
    --chunksize 10000 \
    --min-length 10 \
    --max-length 1000

echo ""
echo "================================================================================"
echo "Step 3/6: Train/Val/Test Split"
echo "================================================================================"
python scripts/task_generation/03_build_splits.py \
    --input data/processed \
    --output data/splits \
    --train-size 0.8 \
    --val-size 0.1 \
    --test-size 0.1

echo ""
echo "================================================================================"
echo "Step 4/6: Training Requirement Detector"
echo "================================================================================"
python scripts/task_generation/04_train_requirement_detector.py \
    --data-dir data/splits \
    --output-dir models/task_gen \
    --model-type sgd

echo ""
echo "================================================================================"
echo "Step 5/6: Training Enrichment Classifiers (Type/Priority/Domain)"
echo "================================================================================"
python scripts/task_generation/05_train_enrichers.py \
    --data-dir data/splits \
    --output-dir models/task_gen \
    --labels type priority domain

echo ""
echo "================================================================================"
echo "Step 6/6: Running Demo"
echo "================================================================================"
python scripts/task_generation/demo_task_generation.py

echo ""
echo "================================================================================"
echo "✅ PIPELINE COMPLETE!"
echo "================================================================================"
echo ""
echo "📦 Models saved to: models/task_gen/"
echo "📊 Reports saved to: report/"
echo ""
echo "Next steps:"
echo "  1. Start API server: python requirement_analyzer/api.py"
echo "  2. Test endpoint: POST http://localhost:8000/generate-tasks"
echo "  3. View docs: http://localhost:8000/docs"
echo ""
echo "================================================================================"
