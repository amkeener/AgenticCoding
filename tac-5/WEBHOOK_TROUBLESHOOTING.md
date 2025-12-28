# Webhook Troubleshooting Guide

## Current Status
✅ **Webhook server is running** on port 8001
⚠️ **Health check shows missing environment variables** (ANTHROPIC_API_KEY required)

## How the Webhook Detection Works

The webhook trigger will ONLY process issues/comments that contain the text **"adw_"** (case-insensitive).

### Detection Flow:
1. GitHub sends webhook event to `/gh-webhook` endpoint
2. Script checks event type:
   - `issues` event with action `opened` - checks issue body
   - `issue_comment` event with action `created` - checks comment body
3. **Key Requirement**: Content must contain `"adw_"` (case-insensitive)
4. If found, calls `adw_classifier` agent to extract workflow type
5. Valid workflows: `adw_plan`, `adw_build`, `adw_test`, `adw_plan_build`, `adw_plan_build_test`

## Common Issues & Solutions

### Issue: Webhook not triggering for your issue

**Checklist:**
1. ✅ Server is running: `curl http://localhost:8001/health`
2. ❓ Issue/comment contains "adw_": Check your issue body includes text like "adw_plan" or "adw_build"
3. ❓ GitHub webhook configured: Go to your repo → Settings → Webhooks → Check if webhook URL is configured
4. ❓ Webhook URL is publicly accessible: GitHub can't reach `localhost:8001` directly

### Issue: Webhook URL not accessible from GitHub

**Solution**: Use Cloudflare Tunnel to expose your local server:

```bash
# 1. Start webhook server (already running)
cd tac-5/adws
uv run adw_triggers/trigger_webhook.py

# 2. In another terminal, expose it via Cloudflare
cd tac-5
./scripts/expose_webhook.sh

# This requires CLOUDFLARED_TUNNEL_TOKEN in .env
```

Then configure GitHub webhook to point to the Cloudflare tunnel URL.

### Issue: Server shows unhealthy status

The health check requires:
- `ANTHROPIC_API_KEY` - Required for Claude Code CLI
- `gh` (GitHub CLI) - Install with `brew install gh` (macOS)

**Fix**:
1. Add `ANTHROPIC_API_KEY` to `.env` file
2. Install GitHub CLI: `brew install gh && gh auth login`
3. Restart webhook server

## Testing the Webhook Locally

You can test if the webhook would trigger by checking your issue:

```bash
# Check if your issue contains "adw_"
# The webhook looks for this exact pattern (case-insensitive)

# Example issue body that WOULD trigger:
"Please use adw_plan to create a plan for this feature"

# Example issue body that would NOT trigger:
"Please create a plan for this feature"  # Missing "adw_"
```

## Manual Testing

Test the webhook endpoint directly:

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test webhook endpoint (simulating GitHub webhook)
curl -X POST http://localhost:8001/gh-webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -d '{
    "action": "opened",
    "issue": {
      "number": 123,
      "body": "This is a test issue with adw_plan workflow"
    }
  }'
```

## Server Logs

Check server logs:
```bash
# If started with nohup
tail -f /tmp/webhook_server.log

# Or check process output if running in foreground
```

## Next Steps

1. **Verify your issue contains "adw_"**: 
   - Edit your GitHub issue and add text containing "adw_plan", "adw_build", etc.
   - Or add a comment with "adw_" text

2. **Configure GitHub webhook**:
   - Go to: https://github.com/amkeener/tac-5/settings/hooks
   - Add webhook with:
     - Payload URL: Your public webhook URL (from Cloudflare tunnel)
     - Content type: `application/json`
     - Events: Select "Issues" and "Issue comments"
     - Active: ✓

3. **Expose webhook publicly**:
   - Run `./scripts/expose_webhook.sh` if you have Cloudflare tunnel token
   - Or use another tunneling service (ngrok, localtunnel, etc.)


