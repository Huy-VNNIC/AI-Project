#!/bin/bash
# Script to test the feedback API endpoints

# Default API URL
API_URL="http://localhost:8001"

# Function to check if the API is running
check_api() {
  echo "Testing API connectivity..."
  curl -s "${API_URL}/api/health" > /dev/null
  if [ $? -ne 0 ]; then
    echo "Error: Cannot connect to the API at ${API_URL}"
    echo "Make sure the service is running with: ./run_estimation_service.sh"
    exit 1
  else
    echo "API is running and accessible."
    echo
  fi
}

# Function to get feedback statistics
get_stats() {
  echo "Fetching feedback statistics..."
  curl -s "${API_URL}/api/feedback/stats" | json_pp
  echo
}

# Function to get feedback overview
get_overview() {
  echo "Fetching feedback overview..."
  curl -s "${API_URL}/api/feedback-overview" | json_pp
  echo
}

# Function to submit sample feedback
submit_feedback() {
  echo "Submitting sample feedback..."
  curl -X POST -H "Content-Type: application/json" -d '{
    "project_id": "sample-project",
    "task_id": "sample-task",
    "requirement_text": "Create a user authentication system with login, registration, and password reset functionality",
    "estimated_effort": 40,
    "actual_effort": 45,
    "effort_unit": "HOUR",
    "model_used": "UCP"
  }' "${API_URL}/api/feedback" | json_pp
  echo
}

# Main script
echo "===== Feedback API Test Tool ====="
echo

# Check if the API is accessible
check_api

# Show menu and handle user input
while true; do
  echo "Please select an option:"
  echo "1. Get feedback statistics"
  echo "2. Get feedback overview and insights"
  echo "3. Submit sample feedback"
  echo "4. Exit"
  echo
  read -p "Enter your choice (1-4): " choice

  case $choice in
    1)
      get_stats
      ;;
    2)
      get_overview
      ;;
    3)
      submit_feedback
      ;;
    4)
      echo "Exiting..."
      exit 0
      ;;
    *)
      echo "Invalid choice. Please try again."
      ;;
  esac

  echo
  read -p "Press Enter to continue..."
  echo
done
