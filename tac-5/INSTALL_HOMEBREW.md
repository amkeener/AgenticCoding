# Install Homebrew

Homebrew requires sudo access and user interaction, so you'll need to run this command in your terminal.

## Installation Command

Copy and paste this command into your terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## What to Expect

1. The installer will prompt you for your password (sudo access required)
2. It will install Homebrew to:
   - `/opt/homebrew` on Apple Silicon Macs (M1/M2/M3)
   - `/usr/local` on Intel Macs
3. It may ask you to add Homebrew to your PATH if it's not already there

## After Installation

Once Homebrew is installed, add it to your PATH if needed:

**For Apple Silicon Macs (arm64):**
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**For Intel Macs:**
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/usr/local/bin/brew shellenv)"
```

## Verify Installation

```bash
brew --version
```

## Install cloudflared

Once Homebrew is installed, you can easily install cloudflared:

```bash
brew install cloudflared
```

## Quick Start Tunnel

After installing cloudflared, start your webhook tunnel:

```bash
cloudflared tunnel --url http://localhost:8001
```

This will display your public webhook URL!



