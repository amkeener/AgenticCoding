#!/bin/bash

# Start webhook server and expose it via Cloudflare tunnel
# This script will:
# 1. Ensure webhook server is running on port 8001
# 2. Start Cloudflare tunnel and display the public URL

set -e

cd "$(dirname "$0")/.."

echo "🚀 Starting Webhook Tunnel..."

# Check if webhook server is running
if ! lsof -ti:8001 > /dev/null 2>&1; then
    echo "⚠️  Webhook server not running on port 8001"
    echo "Starting webhook server in background..."
    cd adws
    nohup uv run adw_triggers/trigger_webhook.py > /tmp/webhook_server.log 2>&1 &
    sleep 2
    cd ..
fi

# Check if cloudflared is available
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not found in PATH"
    echo ""
    echo "Please install cloudflared:"
    echo "  macOS: brew install cloudflared"
    echo "  Or download from: https://github.com/cloudflare/cloudflared/releases"
    echo ""
    echo "Alternative: Use the token-based tunnel:"
    echo "  ./scripts/expose_webhook.sh"
    exit 1
fi

# Load tunnel token from .env
if [ -f .env ]; then
    export $(grep CLOUDFLARED_TUNNEL_TOKEN .env | xargs)
fi

if [ -z "$CLOUDFLARED_TUNNEL_TOKEN" ]; then
    echo "❌ CLOUDFLARED_TUNNEL_TOKEN not found in .env"
    echo "Using quick tunnel instead..."
    echo ""
    echo "🌐 Starting Cloudflare tunnel..."
    echo "Your webhook URL will appear below:"
    echo ""
    cloudflared tunnel --url http://localhost:8001
else
    echo "🌐 Starting Cloudflare tunnel with token..."
    cloudflared tunnel run --token "$CLOUDFLARED_TUNNEL_TOKEN"
fi


