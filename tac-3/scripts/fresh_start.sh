#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Fresh Start: Killing existing instances and starting services...${NC}"

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Step 1: Kill existing processes
echo -e "${YELLOW}Step 1: Killing existing server instances...${NC}"

# Kill processes on ports 8000 (backend) and 5173 (frontend)
echo -e "${GREEN}  → Killing processes on ports 8000 and 5173...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Kill any Python server processes
echo -e "${GREEN}  → Killing Python server processes...${NC}"
pkill -f "python.*server.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "uv run.*server" 2>/dev/null

# Kill any Node/Vite processes
echo -e "${GREEN}  → Killing Node/Vite processes...${NC}"
pkill -f "vite" 2>/dev/null
pkill -f "npm.*dev" 2>/dev/null

# Kill any existing start.sh processes
echo -e "${GREEN}  → Killing existing start scripts...${NC}"
pkill -f "start.sh" 2>/dev/null
pkill -f "fresh_start.sh" 2>/dev/null

# Wait a moment for processes to fully terminate
sleep 2

echo -e "${GREEN}✓ All existing instances killed${NC}"
echo ""

# Step 2: Check prerequisites
echo -e "${YELLOW}Step 2: Checking prerequisites...${NC}"

# Check if .env exists in server directory
if [ ! -f "$PROJECT_ROOT/app/server/.env" ]; then
    echo -e "${RED}✗ Warning: No .env file found in app/server/.${NC}"
    echo "Please:"
    echo "  1. cd app/server"
    echo "  2. cp .env.sample .env"
    echo "  3. Edit .env and add your API keys"
    exit 1
fi
echo -e "${GREEN}  ✓ .env file found${NC}"

# Check if node_modules exists
if [ ! -d "$PROJECT_ROOT/app/client/node_modules" ]; then
    echo -e "${YELLOW}  → Installing client dependencies...${NC}"
    cd "$PROJECT_ROOT/app/client"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install client dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}  ✓ Client dependencies installed${NC}"
else
    echo -e "${GREEN}  ✓ Client dependencies found${NC}"
fi

echo ""

# Step 3: Start services
echo -e "${YELLOW}Step 3: Starting services fresh...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null
    
    # Kill processes on ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    
    # Wait for processes to terminate
    wait
    
    echo -e "${GREEN}✓ Services stopped successfully.${NC}"
    exit 0
}

# Trap EXIT, INT, and TERM signals
trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}  → Starting backend server...${NC}"
cd "$PROJECT_ROOT/app/server"
uv run python server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "     Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start!${NC}"
    exit 1
fi

# Verify backend is responding
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Backend is running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}  ⚠ Backend started but not yet responding (may need more time)${NC}"
fi

# Start frontend
echo -e "${GREEN}  → Starting frontend server...${NC}"
cd "$PROJECT_ROOT/app/client"
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Frontend failed to start!${NC}"
    exit 1
fi

# Verify frontend is responding
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Frontend is running on http://localhost:5173${NC}"
else
    echo -e "${YELLOW}  ⚠ Frontend started but not yet responding (may need more time)${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All services started successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📍 Frontend: http://localhost:5173${NC}"
echo -e "${BLUE}📍 Backend:  http://localhost:8000${NC}"
echo -e "${BLUE}📍 API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services...${NC}"

# Wait for user to press Ctrl+C
wait




