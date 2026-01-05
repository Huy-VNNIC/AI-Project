#!/bin/bash
# Script to fix model version incompatibilities

# Activate virtual environment
source venv/bin/activate

# Install the exact version of scikit-learn used to train the models
pip install scikit-learn==1.7.0

echo "Installed compatible scikit-learn version."
