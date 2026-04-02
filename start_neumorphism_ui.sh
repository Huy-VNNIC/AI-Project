#!/bin/bash
# 🚀 Neumorphism UI - Quick Start Script
# This script starts the FastAPI server with the new Neumorphism UIs

set -e

PROJECT_ROOT="/home/dtu/AI-Project/AI-Project"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🚀 AI Project - Neumorphism UI Quick Start             ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please create it first: python3 -m venv .venv"
    exit 1
fi

# Activate venv
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if FastAPI is installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI not installed!"
    echo "   Installing dependencies..."
    pip install -r config/requirements.txt
fi

# Show available routes
echo ""
echo "📡 Available Routes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🏠 Home Page                  → http://localhost:8000/"
echo "📋 Task Generation            → http://localhost:8000/task-generation"
echo "🧪 Test Case Generator        → http://localhost:8000/testcase-generation"
echo "💬 Feedback & Learning        → http://localhost:8000/test-generation/feedback-ui"
echo "🏥 Health Check               → http://localhost:8000/health"
echo "📚 API Docs                   → http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if port 8000 is already in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use!"
    echo "   Options:"
    echo "   1. Kill existing process: lsof -i :8000 | grep -v PID | awk '{print $2}' | xargs kill"
    echo "   2. Use different port: export API_PORT=8001"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set environment variables
export ENVIRONMENT=development
export API_HOST=0.0.0.0
export API_PORT=8000
export DEFAULT_MODE=model

echo "🔧 Configuration:"
echo "─────────────────────────────────────────────────────────────────"
echo "   Environment: $ENVIRONMENT"
echo "   Host: $API_HOST"
echo "   Port: $API_PORT"
echo "   Default Mode: $DEFAULT_MODE"
echo "─────────────────────────────────────────────────────────────────"
echo ""

# Start FastAPI
echo "🚀 Starting FastAPI server..."
echo "   Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app \
    --host $API_HOST \
    --port $API_PORT \
    --reload \
    --reload-dirs app,requirement_analyzer \
    2>&1 | while IFS= read -r line; do
        # Highlight important messages
        if [[ $line == *"Uvicorn running"* ]]; then
            echo "✅ $line"
        elif [[ $line == *"Application startup complete"* ]]; then
            echo "✅ $line"
        elif [[ $line == *"ERROR"* ]]; then
            echo "❌ $line"
        elif [[ $line == *"WARNING"* ]]; then
            echo "⚠️  $line"
        else
            echo "   $line"
        fi
    done
