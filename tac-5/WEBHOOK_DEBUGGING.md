# Webhook Debugging Guide

## What to Check

### 1. Verify Your Issue/Comment Contains "adw_"

The webhook **only triggers** if the text contains "adw_" (case-insensitive).

✅ **Will trigger:**
- "Please use adw_plan to create a plan"
- "adw_plan_build this feature"
- "Run adw_build with ID abc123"

❌ **Will NOT trigger:**
- "Please create a plan" (missing "adw_")
- "build this feature" (missing "adw_")

### 2. Check GitHub Webhook Configuration

1. Go to: https://github.com/amkeener/tac-5/settings/hooks
2. Click on your webhook
3. Scroll down to "Recent Deliveries"
4. Check if there are any recent events
5. Click on an event to see:
   - **Status**: Should be 200 (success)
   - **Event**: Should be "issues" or "issue_comment"
   - **Payload**: Check if the issue body contains "adw_"

### 3. Check Webhook Server Logs

```bash
tail -f /tmp/webhook_server.log
```

Look for:
- `Received webhook: event=issues, action=opened, issue_number=X`
- `Issue body preview: ...`
- `Contains 'adw_': True/False`

### 4. Required Setup

✅ Webhook server running on port 8001
✅ Cloudflare tunnel active (for public URL)
✅ GitHub webhook configured
✅ Issue/comment contains "adw_"
❌ GitHub CLI (`gh`) - **Install with: `brew install gh`**
✅ ANTHROPIC_API_KEY in .env

## Testing Steps

1. **Install GitHub CLI:**
   ```bash
   brew install gh
   gh auth login
   ```

2. **Restart webhook server:**
   ```bash
   cd /Users/andrewkeener/Documents/AgenticCoding/tac-5/adws
   uv run adw_triggers/trigger_webhook.py
   ```

3. **Start tunnel:**
   ```bash
   cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
   ./start_webhook_tunnel.sh
   ```

4. **Create a test issue** with body:
   ```
   adw_plan
   ```

5. **Watch the logs:**
   ```bash
   tail -f /tmp/webhook_server.log
   ```

## Expected Log Output

When an issue is created with "adw_", you should see:
```
Received webhook: event=issues, action=opened, issue_number=1
Issue body preview: adw_plan
Contains 'adw_': True
Launching adw_plan for issue #1
```

If you don't see this, check:
- GitHub webhook "Recent Deliveries" to see if the event was sent
- Issue body actually contains "adw_"
- Webhook URL is correct in GitHub settings


