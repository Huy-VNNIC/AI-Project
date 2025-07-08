#!/usr/bin/env bash
# Script to run both standard demo and real data demo

echo "Running setup script..."
./setup_multi_model.sh

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r multi_model_integration/requirements.txt

echo ""
echo "========================================================"
echo "Running real data integration demo..."
echo "========================================================"
cd multi_model_integration
python real_data_integration.py

echo ""
echo "========================================================"
echo "Running standard demo integration..."
echo "========================================================"
python demo_integration.py

echo ""
echo "All demos completed successfully!"
