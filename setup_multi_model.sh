#!/usr/bin/env bash
# Setup script for Multi-Model Integration and Agile-Adaptive COCOMO

echo "Setting up environment for Multi-Model Integration and Agile-Adaptive COCOMO..."

# Create and activate virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -r multi_model_integration/requirements.txt

# Create necessary directories
echo "Setting up directory structure..."
mkdir -p models/multi_model
mkdir -p comparison_results/agile_cocomo

# Make demo scripts executable
chmod +x multi_model_integration/demo_integration.py
chmod +x multi_model_integration/real_data_integration.py

echo "Setup complete!"
echo ""
echo "To run the demo:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the demo: python multi_model_integration/demo_integration.py"
