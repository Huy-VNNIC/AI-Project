#!/bin/bash

# Production deployment with Nginx

set -e

echo "🚀 Starting Production Deployment with Nginx..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Create necessary directories
print_status "Setting up production environment..."
mkdir -p models logs uploads datasets/feedback ssl

# Build and start with nginx
print_status "Building and starting services with Nginx..."
docker-compose --profile with-nginx build --no-cache
docker-compose --profile with-nginx down
docker-compose --profile with-nginx up -d

# Wait for services
print_status "Waiting for services to be ready..."
sleep 15

# Check if services are running
if curl -f http://localhost/ > /dev/null 2>&1; then
    print_success "✅ Production AI Estimation Service is running!"
    echo ""
    echo "🌐 Production URLs:"
    echo "   - Main Site: http://localhost (via Nginx)"
    echo "   - Direct API: http://localhost:8000"
    echo "   - COCOMO Form: http://localhost/cocomo"
    echo ""
    echo "🔧 Management Commands:"
    echo "   - View logs: docker-compose --profile with-nginx logs -f"
    echo "   - Stop all: docker-compose --profile with-nginx down"
    echo "   - Restart: docker-compose --profile with-nginx restart"
    echo ""
    echo "📈 Monitoring:"
    echo "   - App logs: docker-compose logs ai-estimation-app"
    echo "   - Nginx logs: docker-compose logs nginx"
else
    print_error "❌ Production deployment failed"
    echo "📋 Checking logs..."
    docker-compose --profile with-nginx logs --tail=30
fi

# Show running containers
echo ""
print_status "Running containers:"
docker-compose --profile with-nginx ps
