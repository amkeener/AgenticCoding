#!/bin/bash
# Install cloudflared CLI binary (not the Python package)

set -e

ARCH=$(uname -m)
OS="darwin"

if [ "$ARCH" = "arm64" ]; then
    BINARY_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64"
elif [ "$ARCH" = "x86_64" ]; then
    BINARY_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

echo "📥 Downloading cloudflared for $ARCH..."
cd /tmp

# Try downloading with curl
if curl -L -f -o cloudflared "$BINARY_URL" 2>/dev/null; then
    echo "✅ Download successful"
elif wget -O cloudflared "$BINARY_URL" 2>/dev/null; then
    echo "✅ Download successful"
else
    echo "❌ Download failed. Please download manually:"
    echo "   $BINARY_URL"
    echo ""
    echo "Then run:"
    echo "   chmod +x cloudflared"
    echo "   mv cloudflared ~/.local/bin/cloudflared"
    exit 1
fi

# Make executable
chmod +x cloudflared

# Verify it works
echo "🔍 Verifying binary..."
if ./cloudflared --version > /dev/null 2>&1; then
    echo "✅ Binary is valid"
else
    echo "❌ Binary verification failed"
    exit 1
fi

# Install to ~/.local/bin
mkdir -p ~/.local/bin
mv cloudflared ~/.local/bin/cloudflared

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "⚠️  ~/.local/bin is not in PATH. Adding to ~/.zshrc..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    export PATH="$HOME/.local/bin:$PATH"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Verify installation:"
echo "   cloudflared --version"
echo ""
echo "If the command is not found, restart your terminal or run:"
echo "   source ~/.zshrc"


