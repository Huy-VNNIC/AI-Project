#!/bin/bash

# AI Estimation Service Docker Deployment Script

set -e

echo "🚀 Starting AI Estimation Service Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available (prefer v2 syntax)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

print_status "Using Docker Compose: $COMPOSE_CMD"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p models logs uploads datasets/feedback ssl

# Build the Docker image
print_status "Building Docker image..."
$COMPOSE_CMD build --no-cache

# Stop any existing containers
print_status "Stopping existing containers..."
$COMPOSE_CMD down

# Start the services
print_status "Starting AI Estimation Service..."
$COMPOSE_CMD up -d

# Wait for service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if service is running
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    print_success "✅ AI Estimation Service is running!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   - Main API: http://localhost:8000"
    echo "   - Alternative: http://localhost:8080"
    echo "   - COCOMO Form: http://localhost:8000/cocomo"
    echo ""
    echo "📊 To view logs: $COMPOSE_CMD logs -f"
    echo "🛑 To stop: $COMPOSE_CMD down"
    echo "🔄 To restart: $COMPOSE_CMD restart"
else
    print_error "❌ Service failed to start properly"
    echo "📋 Checking logs..."
    $COMPOSE_CMD logs --tail=20
fi

# Show running containers
echo ""
print_status "Running containers:"
$COMPOSE_CMD ps
