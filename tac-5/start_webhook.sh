#!/bin/bash
# Combined script to start webhook server and tunnel together

set -e

cd "$(dirname "$0")"

# Add Homebrew to PATH if not already there
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

# Add ~/.local/bin to PATH for Claude Code CLI
export PATH="$HOME/.local/bin:$PATH"

# Source .env file to export environment variables
if [ -f .env ]; then
    set -a  # automatically export all variables
    source .env
    set +a
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting ADW Webhook Server${NC}"

# Check if port 8001 is already in use
if lsof -ti:8001 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8001 is already in use. Killing existing process...${NC}"
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start webhook server in background
echo "📡 Starting webhook server on port 8001..."
cd adws
nohup uv run adw_triggers/trigger_webhook.py > /tmp/webhook_server.log 2>&1 &
WEBHOOK_PID=$!
cd ..

# Wait for server to start
sleep 3

# Check if server started successfully
if ! lsof -ti:8001 > /dev/null 2>&1; then
    echo -e "${YELLOW}❌ Webhook server failed to start. Check logs:${NC}"
    tail -20 /tmp/webhook_server.log
    exit 1
fi

echo -e "${GREEN}✅ Webhook server started (PID: $WEBHOOK_PID)${NC}"
echo "   Logs: tail -f /tmp/webhook_server.log"

# Kill any existing cloudflared tunnels
pkill -f "cloudflared tunnel" 2>/dev/null || true
sleep 1

# Start cloudflared tunnel
echo ""
echo -e "${GREEN}🌐 Starting Cloudflare tunnel...${NC}"
echo "   Press Ctrl+C to stop both services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    kill $WEBHOOK_PID 2>/dev/null || true
    pkill -f "cloudflared tunnel" 2>/dev/null || true
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start tunnel and monitor output
cloudflared tunnel --url http://localhost:8001 2>&1 | while IFS= read -r line; do
    echo "$line"
    
    # Extract and display the URL when it appears
    if echo "$line" | grep -q "trycloudflare.com"; then
        URL=$(echo "$line" | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)
        if [ -n "$URL" ]; then
            echo ""
            echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}✅ Your Webhook URL:${NC}"
            echo "   $URL/gh-webhook"
            echo ""
            echo -e "${GREEN}📋 GitHub Webhook Configuration:${NC}"
            echo "   Payload URL: $URL/gh-webhook"
            echo "   Content Type: application/json"
            echo "   Events: Issues, Issue comments"
            echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
            echo ""
        fi
    fi
done

# If we get here, cleanup
cleanup



