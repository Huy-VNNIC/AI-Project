#!/bin/bash

# AI Estimation Service Management Script

SCRIPT_NAME="AI Estimation Service Manager"
VERSION="1.0.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}    ${SCRIPT_NAME} v${VERSION}${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo ""
}

# Detect Docker Compose command (prefer v2 syntax)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}[ERROR]${NC} Docker Compose not available"
    exit 1
fi

print_menu() {
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}start${NC}       - Start the AI estimation service"
    echo -e "  ${GREEN}stop${NC}        - Stop the service"
    echo -e "  ${GREEN}restart${NC}     - Restart the service"
    echo -e "  ${GREEN}logs${NC}        - View service logs"
    echo -e "  ${GREEN}status${NC}      - Check service status"
    echo -e "  ${GREEN}build${NC}       - Rebuild the Docker image"
    echo -e "  ${GREEN}clean${NC}       - Clean up Docker resources"
    echo -e "  ${GREEN}prod${NC}        - Deploy in production mode (with Nginx)"
    echo -e "  ${GREEN}backup${NC}      - Backup models and data"
    echo -e "  ${GREEN}restore${NC}     - Restore from backup"
    echo -e "  ${GREEN}health${NC}      - Health check"
    echo -e "  ${GREEN}help${NC}        - Show this help message"
    echo ""
}

case "$1" in
    "start")
        echo -e "${BLUE}[INFO]${NC} Starting AI Estimation Service..."
        $COMPOSE_CMD up -d
        sleep 5
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            echo -e "${GREEN}[SUCCESS]${NC} Service started successfully!"
            echo -e "Access at: ${CYAN}http://localhost:8000${NC}"
        else
            echo -e "${RED}[ERROR]${NC} Service failed to start"
            $COMPOSE_CMD logs --tail=10
        fi
        ;;
    "stop")
        echo -e "${BLUE}[INFO]${NC} Stopping AI Estimation Service..."
        $COMPOSE_CMD down
        echo -e "${GREEN}[SUCCESS]${NC} Service stopped"
        ;;
    "restart")
        echo -e "${BLUE}[INFO]${NC} Restarting AI Estimation Service..."
        $COMPOSE_CMD restart
        sleep 5
        echo -e "${GREEN}[SUCCESS]${NC} Service restarted"
        ;;
    "logs")
        echo -e "${BLUE}[INFO]${NC} Showing service logs (Press Ctrl+C to exit)..."
        $COMPOSE_CMD logs -f
        ;;
    "status")
        echo -e "${BLUE}[INFO]${NC} Checking service status..."
        $COMPOSE_CMD ps
        echo ""
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            echo -e "${GREEN}[HEALTHY]${NC} Service is responding"
        else
            echo -e "${RED}[UNHEALTHY]${NC} Service is not responding"
        fi
        ;;
    "build")
        echo -e "${BLUE}[INFO]${NC} Rebuilding Docker image..."
        $COMPOSE_CMD build --no-cache
        echo -e "${GREEN}[SUCCESS]${NC} Image rebuilt"
        ;;
    "clean")
        echo -e "${BLUE}[INFO]${NC} Cleaning up Docker resources..."
        $COMPOSE_CMD down --volumes --remove-orphans
        docker system prune -f
        echo -e "${GREEN}[SUCCESS]${NC} Cleanup completed"
        ;;
    "prod")
        echo -e "${BLUE}[INFO]${NC} Starting production deployment..."
        chmod +x deploy-production.sh
        ./deploy-production.sh
        ;;
    "backup")
        echo -e "${BLUE}[INFO]${NC} Creating backup..."
        BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
        BACKUP_DIR="backup_${BACKUP_DATE}"
        mkdir -p "$BACKUP_DIR"
        
        # Backup models and datasets
        if [ -d "models" ]; then
            cp -r models "$BACKUP_DIR/"
        fi
        if [ -d "datasets" ]; then
            cp -r datasets "$BACKUP_DIR/"
        fi
        if [ -d "uploads" ]; then
            cp -r uploads "$BACKUP_DIR/"
        fi
        
        # Create archive
        tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
        rm -rf "$BACKUP_DIR"
        
        echo -e "${GREEN}[SUCCESS]${NC} Backup created: ${BACKUP_DIR}.tar.gz"
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo -e "${RED}[ERROR]${NC} Please specify backup file: ./manage.sh restore backup_file.tar.gz"
            exit 1
        fi
        
        if [ ! -f "$2" ]; then
            echo -e "${RED}[ERROR]${NC} Backup file not found: $2"
            exit 1
        fi
        
        echo -e "${BLUE}[INFO]${NC} Restoring from backup: $2"
        tar -xzf "$2"
        BACKUP_DIR=$(basename "$2" .tar.gz)
        
        if [ -d "${BACKUP_DIR}/models" ]; then
            cp -r "${BACKUP_DIR}/models" ./
        fi
        if [ -d "${BACKUP_DIR}/datasets" ]; then
            cp -r "${BACKUP_DIR}/datasets" ./
        fi
        if [ -d "${BACKUP_DIR}/uploads" ]; then
            cp -r "${BACKUP_DIR}/uploads" ./
        fi
        
        rm -rf "$BACKUP_DIR"
        echo -e "${GREEN}[SUCCESS]${NC} Restore completed"
        ;;
    "health")
        echo -e "${BLUE}[INFO]${NC} Performing health check..."
        
        # Check Docker
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}[FAIL]${NC} Docker not installed"
            exit 1
        fi
        echo -e "${GREEN}[OK]${NC} Docker is available"
        
        # Check Docker Compose
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo -e "${RED}[FAIL]${NC} Docker Compose not available"
            exit 1
        fi
        echo -e "${GREEN}[OK]${NC} Docker Compose is available"
        
        # Check service
        if curl -f http://localhost:8000/ > /dev/null 2>&1; then
            echo -e "${GREEN}[OK]${NC} AI Estimation Service is responding"
        else
            echo -e "${YELLOW}[WARNING]${NC} Service is not responding (may not be started)"
        fi
        
        # Check models
        if [ -d "models" ] && [ "$(ls -A models)" ]; then
            echo -e "${GREEN}[OK]${NC} Models directory exists and has content"
        else
            echo -e "${YELLOW}[WARNING]${NC} Models directory is empty or missing"
        fi
        
        echo -e "${GREEN}[SUCCESS]${NC} Health check completed"
        ;;
    "help"|""|*)
        print_header
        print_menu
        echo -e "${YELLOW}Usage:${NC}"
        echo -e "  ./manage.sh <command>"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo -e "  ./manage.sh start          # Start the service"
        echo -e "  ./manage.sh prod           # Production deployment"
        echo -e "  ./manage.sh backup         # Create backup"
        echo -e "  ./manage.sh restore backup.tar.gz  # Restore backup"
        echo ""
        ;;
esac
