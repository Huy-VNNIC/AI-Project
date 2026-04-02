#!/bin/bash
# Setup and run script for Rule-Based Test Case Generator
# Usage: bash setup_and_run.sh

set -e

echo "======================================================================"
echo "🚀 RULE-BASED TEST CASE GENERATOR - SETUP & RUN"
echo "======================================================================"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "
📂 Working directory: $SCRIPT_DIR
"

# Step 1: Install requirements
echo "======================================================================"
echo "Step 1: Installing Python Dependencies"
echo "======================================================================"

echo "📦 Installing requirements.txt..."
python3 -m pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" | grep -v "Requirement already" || true
echo "✅ Dependencies installed"

# Step 2: Download spaCy model
echo "
======================================================================"
echo "Step 2: Downloading spaCy Model"
echo "======================================================================"

echo "📦 Downloading en_core_web_sm..."
python3 -m spacy download -q en_core_web_sm
echo "✅ spaCy model downloaded"

# Step 3: Run quick start
echo "
======================================================================"
echo "Step 3: Running Quick Start Demo"
echo "======================================================================"

python3 setup.py

echo "
======================================================================"
echo "✨ ALL COMPLETE!"
echo "======================================================================"
