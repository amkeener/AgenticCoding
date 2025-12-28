# Webhook Public URL Configuration

## Current Status
✅ Webhook server is running on `localhost:8001`

## To Expose Publicly and Get URL

### Option 1: Cloudflare Tunnel (Recommended if you have cloudflared installed)

Run this command:
```bash
cloudflared tunnel --url http://localhost:8001
```

You'll see output like:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://random-name-1234.trycloudflare.com                                               |
+--------------------------------------------------------------------------------------------+
```

**Your Payload URL will be**: `https://random-name-1234.trycloudflare.com/gh-webhook`

### Option 2: If you have CLOUDFLARED_TUNNEL_TOKEN configured

Run:
```bash
cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
./scripts/expose_webhook.sh
```

This will start a persistent tunnel. The URL will be shown in the output or you can find it in your Cloudflare dashboard.

## GitHub Webhook Configuration

Once you have your public URL:

### Payload URL
```
https://YOUR-TUNNEL-URL.trycloudflare.com/gh-webhook
```

### Content Type
```
application/json
```

### Events to Subscribe To
- ✅ Issues (opened)
- ✅ Issue comments (created)

## Quick Test

After configuring the webhook, test it by creating an issue with:
```
Please use adw_plan to create a plan
```

The webhook will trigger if it sees "adw_" in the issue text.


