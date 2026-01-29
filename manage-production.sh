#!/bin/bash

# Production API Container Management Script
# Manages the requirement-analyzer-api Docker container

set -e

CONTAINER_NAME="requirement-analyzer-api"
IMAGE_NAME="requirement-analyzer:production"
PORT=8000

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_status() {
    echo -e "\n${BLUE}📊 Container Status:${NC}"
    docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

start_container() {
    echo -e "${GREEN}🚀 Starting container...${NC}"
    
    # Check if container exists
    if docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        echo "Container exists, starting..."
        docker start $CONTAINER_NAME
    else
        echo "Creating new container..."
        docker run -d \
            --name $CONTAINER_NAME \
            -p $PORT:$PORT \
            -v "$PWD/logs:/app/logs" \
            -v "$PWD/datasets/feedback:/app/datasets/feedback" \
            -v "$PWD/processed_data:/app/processed_data" \
            --restart unless-stopped \
            --health-cmd "python -c 'import requests; requests.get(\"http://localhost:8000/health\")'" \
            --health-interval 30s \
            --health-timeout 10s \
            --health-retries 3 \
            $IMAGE_NAME
    fi
    
    echo -e "${GREEN}✓ Container started${NC}"
    show_status
}

stop_container() {
    echo -e "${YELLOW}🛑 Stopping container...${NC}"
    docker stop $CONTAINER_NAME || true
    echo -e "${GREEN}✓ Container stopped${NC}"
    show_status
}

restart_container() {
    echo -e "${YELLOW}🔄 Restarting container...${NC}"
    docker restart $CONTAINER_NAME
    echo -e "${GREEN}✓ Container restarted${NC}"
    show_status
}

remove_container() {
    echo -e "${RED}🗑️  Removing container...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}✓ Container removed${NC}"
}

view_logs() {
    echo -e "${BLUE}📋 Container Logs (press Ctrl+C to exit):${NC}"
    docker logs -f $CONTAINER_NAME
}

check_health() {
    echo -e "${BLUE}🏥 Health Check:${NC}"
    
    # Check container status
    if ! docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
        echo -e "${RED}✗ Container is not running${NC}"
        return 1
    fi
    
    # Check health endpoint
    if curl -sf http://localhost:$PORT/health > /dev/null; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        curl http://localhost:$PORT/health
        echo
    else
        echo -e "${RED}✗ API is not responding${NC}"
        return 1
    fi
}

rebuild_and_restart() {
    echo -e "${BLUE}🔨 Rebuilding image and restarting...${NC}"
    
    # Stop and remove existing container
    remove_container
    
    # Kill any process on port
    echo "Checking port $PORT..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || echo "Port $PORT is free"
    
    # Rebuild image
    echo -e "${BLUE}Building new image...${NC}"
    docker build -f Dockerfile.api-production -t $IMAGE_NAME .
    
    # Start new container
    start_container
    
    # Wait and check health
    echo "Waiting for service to start..."
    sleep 10
    check_health
}

case "${1:-}" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    remove)
        remove_container
        ;;
    logs)
        view_logs
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    rebuild)
        rebuild_and_restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|remove|logs|status|health|rebuild}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the container"
        echo "  stop     - Stop the container"
        echo "  restart  - Restart the container"
        echo "  remove   - Stop and remove the container"
        echo "  logs     - View container logs (follow mode)"
        echo "  status   - Show container status"
        echo "  health   - Check API health"
        echo "  rebuild  - Rebuild image and restart container"
        exit 1
        ;;
esac
