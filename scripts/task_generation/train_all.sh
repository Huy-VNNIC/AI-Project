#!/bin/bash
# Master script to run complete task generation training pipeline
# Usage: bash scripts/task_generation/train_all.sh [dataset_size]
# dataset_size: small (10k), medium (100k), large (1m)

set -e  # Exit on error

DATASET_SIZE=${1:-medium}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "======================================================================"
echo "🚀 TASK GENERATION TRAINING PIPELINE"
echo "======================================================================"
echo "Project root: $PROJECT_ROOT"
echo "Dataset size: $DATASET_SIZE"
echo ""

# Activate virtual environment
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo "🐍 Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Set dataset path
case $DATASET_SIZE in
    small)
        DATASET_PATH="requirement_analyzer/dataset_small_10k"
        ;;
    medium)
        DATASET_PATH="requirement_analyzer/dataset_medium_100k"
        ;;
    large)
        DATASET_PATH="requirement_analyzer/dataset_large_1m"
        ;;
    *)
        echo "❌ Invalid dataset size: $DATASET_SIZE"
        echo "   Valid options: small, medium, large"
        exit 1
        ;;
esac

echo "📂 Dataset: $DATASET_PATH"
echo ""

# Check if dataset exists
if [ ! -d "$PROJECT_ROOT/$DATASET_PATH" ]; then
    echo "❌ Dataset not found: $PROJECT_ROOT/$DATASET_PATH"
    exit 1
fi

# Step 1: Scan dataset
echo "======================================================================"
echo "📊 STEP 1/5: Scanning Dataset"
echo "======================================================================"
python "$PROJECT_ROOT/scripts/task_generation/01_scan_dataset.py" \
    --dataset "$DATASET_PATH" \
    --output "report/data_quality_report_${DATASET_SIZE}" \
    --chunksize 10000

echo ""
echo "✅ Step 1 complete. Check report/data_quality_report_${DATASET_SIZE}.md"
echo ""

# Step 2: Build parquet
echo "======================================================================"
echo "🧹 STEP 2/5: Cleaning and Building Parquet"
echo "======================================================================"
python "$PROJECT_ROOT/scripts/task_generation/02_build_parquet.py" \
    --input "$DATASET_PATH" \
    --output "data/processed_${DATASET_SIZE}" \
    --chunksize 10000 \
    --min-length 10 \
    --max-length 1000

echo ""
echo "✅ Step 2 complete. Data saved to data/processed_${DATASET_SIZE}/"
echo ""

# Step 3: Build splits
echo "======================================================================"
echo "🔀 STEP 3/5: Creating Train/Val/Test Splits"
echo "======================================================================"
python "$PROJECT_ROOT/scripts/task_generation/03_build_splits.py" \
    --input "data/processed_${DATASET_SIZE}" \
    --output "data/splits_${DATASET_SIZE}" \
    --train-size 0.8 \
    --val-size 0.1 \
    --test-size 0.1 \
    --random-state 42

echo ""
echo "✅ Step 3 complete. Splits saved to data/splits_${DATASET_SIZE}/"
echo ""

# Step 4: Train requirement detector
echo "======================================================================"
echo "🎯 STEP 4/5: Training Requirement Detector"
echo "======================================================================"
python "$PROJECT_ROOT/scripts/task_generation/04_train_requirement_detector.py" \
    --data-dir "data/splits_${DATASET_SIZE}" \
    --output-dir "models/task_gen_${DATASET_SIZE}" \
    --model-type sgd

echo ""
echo "✅ Step 4 complete. Model saved to models/task_gen_${DATASET_SIZE}/"
echo ""

# Step 5: Train enrichers
echo "======================================================================"
echo "🏷️  STEP 5/5: Training Enrichment Classifiers"
echo "======================================================================"
python "$PROJECT_ROOT/scripts/task_generation/05_train_enrichers.py" \
    --data-dir "data/splits_${DATASET_SIZE}" \
    --output-dir "models/task_gen_${DATASET_SIZE}" \
    --labels type priority domain

echo ""
echo "✅ Step 5 complete. Models saved to models/task_gen_${DATASET_SIZE}/"
echo ""

# Create symlink to latest models
echo "======================================================================"
echo "🔗 Creating symlink to models..."
echo "======================================================================"
rm -f "$PROJECT_ROOT/models/task_gen"
ln -s "task_gen_${DATASET_SIZE}" "$PROJECT_ROOT/models/task_gen"
echo "✅ Symlink created: models/task_gen -> models/task_gen_${DATASET_SIZE}"
echo ""

# Summary
echo "======================================================================"
echo "🎉 TRAINING COMPLETE!"
echo "======================================================================"
echo ""
echo "📦 Models location: models/task_gen_${DATASET_SIZE}/"
echo "   - requirement_detector_model.joblib"
echo "   - type_model.joblib"
echo "   - priority_model.joblib"
echo "   - domain_model.joblib"
echo ""
echo "📊 Check metrics:"
echo "   cat models/task_gen_${DATASET_SIZE}/requirement_detector_metrics.json"
echo "   cat models/task_gen_${DATASET_SIZE}/enrichers_summary.json"
echo ""
echo "🧪 Test the pipeline:"
echo "   python demo_task_generation.py"
echo ""
echo "🚀 Start API server:"
echo "   python requirement_analyzer/api.py"
echo ""
echo "======================================================================"
