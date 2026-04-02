#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
clear
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║    STARTING UNIFIED TEST & TASK GENERATION SYSTEM             ║"
echo "║                                                               ║"
echo "║  📱 Main System (Port 8000)                                   ║"
echo "║     - Requirement Analysis                                    ║"
echo "║     - Task Generation                                         ║"
echo "║     - Test Case Generation (Integrated)                       ║"
echo "║     - Unified Web Interface                                   ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

PROJECT_DIR="/home/dtu/AI-Project/AI-Project"
cd "$PROJECT_DIR"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Kill processes on port 8000 if they exist
echo -e "${YELLOW}Checking for existing processes on port 8000...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}Killing process on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

sleep 1

# Start Main System (port 8000)
echo -e "${GREEN}Starting Main System on port 8000...${NC}"
echo -e "${GREEN}(Requirement Analyzer + Test Generator + Unified UI)${NC}"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
MAIN_PID=$!
sleep 5

cd "$PROJECT_DIR"

# Print startup summary
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SYSTEM STARTED                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📱 Access the system:${NC}"
echo -e "  ${GREEN}Unified Web Interface:${NC}  http://localhost:8000"
echo -e "  ${GREEN}API Documentation:${NC}      http://localhost:8000/docs"
echo -e "  ${GREEN}Dashboard:${NC}              http://localhost:8000/dashboard"
echo ""
echo -e "${YELLOW}Process ID:${NC}"
echo "  Main System: $MAIN_PID"
echo ""
echo -e "${YELLOW}To stop the system, press Ctrl+C${NC}"
echo ""

# Wait for the process
wait

echo -e "${YELLOW}System stopped.${NC}"

