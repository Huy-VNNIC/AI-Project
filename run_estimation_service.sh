#!/bin/bash
# Script to run the production-ready effort estimation service with feedback system

# Default values
HOST="0.0.0.0"
PORT=8001
DEBUG=false
PRODUCTION=true
LOG_FILE="effort_estimation_service.log"

# Display help information
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --host HOST         Host to run the server on (default: 0.0.0.0)"
    echo "  --port PORT         Port to run the server on (default: 8001)"
    echo "  --debug             Run in debug mode (default: false)"
    echo "  --no-production     Run in development mode without Waitress"
    echo "  --help              Display this help and exit"
    echo ""
}

# Process command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    --no-production)
      PRODUCTION=false
      shift
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Set up production flag
if [ "$PRODUCTION" = true ]; then
    PROD_FLAG="--production"
else
    PROD_FLAG=""
fi

# Set up debug flag
if [ "$DEBUG" = true ]; then
    DEBUG_FLAG="--debug"
else
    DEBUG_FLAG=""
fi

# Check for virtual environment and activate it
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate" || {
        echo "Failed to activate virtual environment. Please check $VENV_DIR directory."
        exit 1
    }
    echo "Virtual environment activated successfully."
else
    echo "Warning: Virtual environment directory ($VENV_DIR) not found."
    echo "Checking for system-wide dependencies instead..."
    
    # Check if pip3 exists, otherwise try pip
    if command -v pip3 &>/dev/null; then
        PIP_CMD="pip3"
    else
        PIP_CMD="pip"
    fi
    
    # Ensure required Python packages are installed
    $PIP_CMD install -q waitress flask flask-cors scikit-learn pandas numpy || {
        echo "Failed to install dependencies. Please check requirements.txt and try again."
        exit 1
    }
fi

# Print service information
echo "====================================================================="
echo "Starting Software Effort Estimation Service (Production)"
echo "====================================================================="
echo "Host: $HOST"
echo "Port: $PORT"
echo "Debug mode: $DEBUG"
echo "Production mode: $PRODUCTION"
echo "Log file: $LOG_FILE"
echo "====================================================================="

# Start the service - use python3 explicitly to avoid confusion
echo "Launching service..."
python3 run_estimation_service.py --host "$HOST" --port "$PORT" $DEBUG_FLAG $PROD_FLAG

# Deactivate virtual environment if it was activated
if [ -d "$VENV_DIR" ]; then
    deactivate 2>/dev/null || true
fi
