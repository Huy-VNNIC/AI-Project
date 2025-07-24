#!/bin/bash
# Script to run the effort estimation service

# Default port
PORT=5000

# Process command-line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --skip-integration)
      SKIP_INTEGRATION="--skip-integration"
      shift
      ;;
    --task-service-url)
      TASK_SERVICE_URL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set default task service URL if not specified
if [ -z "$TASK_SERVICE_URL" ]; then
  TASK_SERVICE_URL="http://localhost:8000"
fi

# Run the service
echo "Starting effort estimation service on port $PORT..."
python requirement_analyzer/service_integration.py --port $PORT --task-service-url $TASK_SERVICE_URL $SKIP_INTEGRATION
