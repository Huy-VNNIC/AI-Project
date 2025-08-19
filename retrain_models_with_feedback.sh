#!/bin/bash
# Script to periodically retrain models with feedback data

# Set the working directory to the project root
cd "$(dirname "$0")" || exit 1

# Create logs directory if it doesn't exist
mkdir -p logs

# Log file
LOG_FILE="logs/retrain_cron_$(date +%Y%m%d_%H%M%S).log"

echo "=== Starting model retraining - $(date) ===" >> "$LOG_FILE"

# Activate virtual environment if using one
# source venv/bin/activate

# Run the retraining script
python scheduled_retraining.py --notify 2>&1 >> "$LOG_FILE"
RESULT=$?

echo "=== Retraining finished with exit code $RESULT - $(date) ===" >> "$LOG_FILE"

# Email notification for errors (optional)
if [ $RESULT -ne 0 ]; then
    echo "Retraining failed. Check logs at $LOG_FILE"
    
    # Uncomment to enable email notifications for failures
    # mail -s "AI Model Retraining Failed" admin@example.com < "$LOG_FILE"
fi

exit $RESULT
