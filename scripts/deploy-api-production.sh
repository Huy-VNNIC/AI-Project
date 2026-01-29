#!/bin/bash
# Production deployment script for Requirements Engineering API

set -e

echo "🚀 Starting production deployment..."

# Configuration
CONTAINER_NAME="requirement-analyzer-api"
IMAGE_NAME="requirement-analyzer:production"
PORT=8000

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Stop and remove existing container
echo -e "${YELLOW}📦 Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Step 2: Kill any process using port 8000
echo -e "${YELLOW}🔫 Killing processes on port $PORT...${NC}"
lsof -ti:$PORT | xargs kill -9 2>/dev/null || echo "Port $PORT is free"

# Step 3: Build Docker image
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
docker build -f Dockerfile.api-production -t $IMAGE_NAME .

# Step 4: Start container with docker-compose
echo -e "${YELLOW}🚢 Starting container...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Step 5: Wait for health check
echo -e "${YELLOW}⏳ Waiting for API to be ready...${NC}"
sleep 10

# Step 6: Test health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:$PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy!${NC}"
        break
    else
        echo "Retrying... ($((RETRY_COUNT+1))/$MAX_RETRIES)"
        sleep 5
        RETRY_COUNT=$((RETRY_COUNT+1))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ API failed to start properly${NC}"
    echo "Checking logs..."
    docker-compose -f docker-compose.production.yml logs api
    exit 1
fi

# Step 7: Test V2 health endpoint
echo -e "${YELLOW}🏥 Testing V2 endpoint...${NC}"
curl -s http://localhost:$PORT/api/v2/task-generation/health | python3 -m json.tool

# Step 8: Show status
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📊 Container status:"
docker-compose -f docker-compose.production.yml ps
echo ""
echo "🌐 API Endpoints:"
echo "   - Health: http://localhost:$PORT/health"
echo "   - V2 Health: http://localhost:$PORT/api/v2/task-generation/health"
echo "   - API Docs: http://localhost:$PORT/docs"
echo "   - V2 Generate: http://localhost:$PORT/api/v2/task-generation/generate-from-file"
echo ""
echo "📝 View logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f api"
echo ""
echo "🛑 Stop deployment:"
echo "   docker-compose -f docker-compose.production.yml down"
echo ""

# Optional: Show server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo -e "${YELLOW}🌍 External access:${NC}"
echo "   http://$SERVER_IP:$PORT"
echo "   http://103.141.177.146:$PORT"
