#!/bin/bash

# Build and Run AI Estimation API with Docker

echo "🚀 Building AI Estimation API Docker Container..."

# Stop any running containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.api.yml down

# Remove old images (optional)
echo "Removing old images..."
docker rmi ai-project-ai-estimation-api 2>/dev/null || true

# Build the Docker image
echo "Building new Docker image..."
docker-compose -f docker-compose.api.yml build --no-cache

# Start the services
echo "Starting AI Estimation API..."
docker-compose -f docker-compose.api.yml up -d

# Wait for service to be ready
echo "Waiting for service to start..."
sleep 10

# Check if service is running
if docker-compose -f docker-compose.api.yml ps | grep -q "Up"; then
    echo "✅ AI Estimation API is running successfully!"
    echo ""
    echo "📊 Service Information:"
    echo "- API URL: http://localhost:8000"
    echo "- API Documentation: http://localhost:8000/docs"
    echo "- Alternative URL: http://localhost:8080"
    echo ""
    echo "🔍 Container Status:"
    docker-compose -f docker-compose.api.yml ps
    echo ""
    echo "📝 To view logs: docker-compose -f docker-compose.api.yml logs -f"
    echo "🛑 To stop: docker-compose -f docker-compose.api.yml down"
else
    echo "❌ Failed to start the service. Check logs:"
    docker-compose -f docker-compose.api.yml logs
fi