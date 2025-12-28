# Webhook Setup - Quick Start

## Single Command to Start Everything

```bash
cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
./start_webhook.sh
```

This single script will:
1. ✅ Start the webhook server on port 8001
2. ✅ Start the Cloudflare tunnel to expose it publicly
3. ✅ Display your webhook URL when ready
4. ✅ Handle cleanup when you press Ctrl+C

## What Each Component Does

- **Webhook Server** (`trigger_webhook.py`): Listens on `localhost:8001` for GitHub webhook events
- **Cloudflare Tunnel** (`cloudflared`): Exposes `localhost:8001` to the internet so GitHub can send webhooks

You need both running for the webhook to work!

## GitHub Webhook Configuration

Once you see the URL from `./start_webhook.sh`:

1. Go to: https://github.com/amkeener/tac-5/settings/hooks
2. Add webhook:
   - **Payload URL**: `https://YOUR-URL.trycloudflare.com/gh-webhook`
   - **Content Type**: `application/json`
   - **Events**: Select "Issues" and "Issue comments"
   - **Active**: ✓

## Testing

Create a GitHub issue with body containing "adw_":
```
adw_plan
```

The webhook will trigger and process the workflow automatically!

## Stopping

Press `Ctrl+C` in the terminal where `./start_webhook.sh` is running. It will clean up both processes automatically.

## Logs

- Webhook server logs: `tail -f /tmp/webhook_server.log`
- Health check: `curl http://localhost:8001/health`


