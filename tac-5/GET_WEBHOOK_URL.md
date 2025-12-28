# Get Your Webhook Public URL

## Current Status
✅ **Webhook server is running** on `localhost:8001`

## Install Cloudflared

Since cloudflared isn't installed yet, install it:

**macOS (Homebrew - if you have it):**
```bash
brew install cloudflared
```

**macOS (Manual download):**
1. Go to: https://github.com/cloudflare/cloudflared/releases/latest
2. Download: `cloudflared-darwin-arm64` (or `cloudflared-darwin-amd64` if Intel Mac)
3. Move to a location in your PATH:
   ```bash
   chmod +x cloudflared
   mv cloudflared ~/.local/bin/cloudflared
   ```

## Start the Tunnel

Once cloudflared is installed, run:

```bash
cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
cloudflared tunnel --url http://localhost:8001
```

You'll see output like:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://abc123-xyz.trycloudflare.com                                                     |
+--------------------------------------------------------------------------------------------+
```

## GitHub Webhook Configuration

Once you have the URL from above:

### Payload URL
```
https://abc123-xyz.trycloudflare.com/gh-webhook
```
*(Replace with your actual tunnel URL)*

### Content Type
```
application/json
```

### Which events would you like to trigger this webhook?
- ✅ **Issues** (check this)
- ✅ **Issue comments** (check this)
- ❌ Uncheck everything else

### Active
✅ (checked)

## Alternative: Use Your Cloudflare Tunnel Token

If you have `CLOUDFLARED_TUNNEL_TOKEN` in your `.env` file:

```bash
cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
./scripts/expose_webhook.sh
```

This will start a persistent tunnel. Check your Cloudflare dashboard for the URL, or look at the tunnel output.

## Test

After configuring, create a test GitHub issue with the text:
```
Please use adw_plan to create a plan
```

The webhook will detect "adw_" and trigger the workflow!


