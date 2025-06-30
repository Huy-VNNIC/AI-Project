#!/bin/bash
# cocomo_setup.sh - Script to setup and run COCOMO II predictor

echo "===== COCOMO II Extended Setup and Demo ====="
echo ""

# Set paths
PROJECT_DIR=$(pwd)
MODELS_DIR="$PROJECT_DIR/models/cocomo_ii_extended"
PROCESSED_DATA_DIR="$PROJECT_DIR/processed_data"

# Check environment
echo "Checking environment..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3 to continue."
    exit 1
fi

# Create directories if they don't exist
if [ ! -d "$PROCESSED_DATA_DIR" ]; then
    echo "Creating processed_data directory..."
    mkdir -p "$PROCESSED_DATA_DIR"
fi

if [ ! -d "$MODELS_DIR" ]; then
    echo "Creating models directory..."
    mkdir -p "$MODELS_DIR"
fi

# Menu
echo ""
echo "What would you like to do?"
echo "1. Run COCOMO II Demo (uses simplified formulas)"
echo "2. Create dummy model files (for testing only)"
echo "3. Check environment"
echo "4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Running COCOMO II Demo..."
        python3 demo.py
        ;;
    2)
        echo "Creating dummy model files..."
        mkdir -p "$MODELS_DIR"
        
        # Create a simple dummy model file
        echo "{\"model\": \"dummy\"}" > "$MODELS_DIR/config.json"
        echo "Dummy model files created in $MODELS_DIR"
        echo "Note: These are not trained on real data and are for demonstration only."
        ;;
    3)
        echo "Checking environment..."
        echo "Python version:"
        python3 --version
        
        echo ""
        echo "Project structure:"
        ls -la $PROJECT_DIR
        
        echo ""
        echo "Processed data directory:"
        if [ -d "$PROCESSED_DATA_DIR" ]; then
            ls -la $PROCESSED_DATA_DIR
        else
            echo "Directory does not exist yet."
        fi
        
        echo ""
        echo "Models directory:"
        if [ -d "$MODELS_DIR" ]; then
            ls -la $MODELS_DIR
        else
            echo "Directory does not exist yet."
        fi
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "===== Setup Complete ====="
