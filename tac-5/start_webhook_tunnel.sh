#!/bin/bash
# Start cloudflared tunnel and display the webhook URL

# Add Homebrew to PATH if not already there
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -f /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
fi

echo "🌐 Starting Cloudflare tunnel for webhook..."
echo ""

# Start tunnel and capture URL
cloudflared tunnel --url http://localhost:8001 2>&1 | while IFS= read -r line; do
    echo "$line"
    
    # Extract and display the URL when it appears
    if echo "$line" | grep -q "trycloudflare.com"; then
        URL=$(echo "$line" | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | head -1)
        if [ -n "$URL" ]; then
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            echo "✅ Your Webhook URL:"
            echo "   $URL/gh-webhook"
            echo ""
            echo "📋 GitHub Webhook Configuration:"
            echo "   Payload URL: $URL/gh-webhook"
            echo "   Content Type: application/json"
            echo "   Events: Issues, Issue comments"
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
        fi
    fi
done
