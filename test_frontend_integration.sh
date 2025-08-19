#!/bin/bash
# This script tests the integration between the Next.js frontend and the AI service backend

# Configuration
AI_SERVICE_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"
API_KEY="test-api-key"  # Replace with actual API key if needed

# Text colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
  local url=$1
  local name=$2
  
  echo -e "${YELLOW}Checking if $name is running...${NC}"
  
  curl -s --head --request GET $url > /dev/null
  if [ $? -ne 0 ]; then
    echo -e "${RED}❌ $name is not running at $url${NC}"
    echo -e "${YELLOW}Please start the $name and try again${NC}"
    return 1
  else
    echo -e "${GREEN}✅ $name is running at $url${NC}"
    return 0
  fi
}

# Test the AI service health endpoint
test_ai_service_health() {
  echo -e "\n${YELLOW}Testing AI service health endpoint...${NC}"
  
  response=$(curl -s "${AI_SERVICE_URL}/api/health")
  if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to connect to AI service health endpoint${NC}"
    return 1
  fi
  
  if echo "$response" | grep -q "\"status\":[[:space:]]*\"ok\""; then
    echo -e "${GREEN}✅ AI service health check passed${NC}"
    echo "Response: $response"
    return 0
  else
    echo -e "${RED}❌ AI service health check failed${NC}"
    echo "Response: $response"
    return 1
  fi
}

# Test the frontend API proxy
test_frontend_api_proxy() {
  echo -e "\n${YELLOW}Testing frontend API proxy...${NC}"
  
  response=$(curl -s "${FRONTEND_URL}/api/health")
  if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to connect to frontend API proxy${NC}"
    return 1
  fi
  
  if echo "$response" | grep -q "\"status\":[[:space:]]*\"ok\""; then
    echo -e "${GREEN}✅ Frontend API proxy test passed${NC}"
    echo "Response: $response"
    return 0
  else
    echo -e "${RED}❌ Frontend API proxy test failed${NC}"
    echo "Response: $response"
    return 1
  fi
}

# Test the feedback stats endpoint
test_feedback_stats() {
  echo -e "\n${YELLOW}Testing feedback stats endpoint...${NC}"
  
  ai_response=$(curl -s "${AI_SERVICE_URL}/api/feedback/stats")
  frontend_response=$(curl -s "${FRONTEND_URL}/api/feedback")
  
  echo -e "${GREEN}AI Service Response:${NC}"
  echo "$ai_response" | json_pp
  
  echo -e "${GREEN}Frontend Proxy Response:${NC}"
  echo "$frontend_response" | json_pp
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Feedback stats endpoint test completed${NC}"
    return 0
  else
    echo -e "${RED}❌ Feedback stats endpoint test failed${NC}"
    return 1
  fi
}

# Main function
main() {
  echo -e "${GREEN}=== Frontend-Backend Integration Test ===${NC}"
  
  # Check if services are running
  check_service "$AI_SERVICE_URL" "AI Service"
  ai_service_running=$?
  
  check_service "$FRONTEND_URL" "Next.js Frontend"
  frontend_running=$?
  
  # If either service is not running, exit
  if [ $ai_service_running -ne 0 ] || [ $frontend_running -ne 0 ]; then
    echo -e "${RED}One or more required services are not running. Exiting.${NC}"
    exit 1
  fi
  
  # Run tests
  test_ai_service_health
  test_frontend_api_proxy
  test_feedback_stats
  
  echo -e "\n${GREEN}=== Integration Test Complete ===${NC}"
}

# Run the main function
main
