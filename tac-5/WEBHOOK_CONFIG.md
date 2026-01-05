# GitHub Webhook Configuration

## Quick Setup Instructions

### 1. Start the Webhook Tunnel

Run this command to start the webhook server and expose it publicly:

```bash
cd /Users/andrewkeener/Documents/AgenticCoding/tac-5
./scripts/start_webhook_tunnel.sh
```

Or if you have a Cloudflare tunnel token configured:

```bash
./scripts/expose_webhook.sh
```

### 2. Get Your Public Webhook URL

After starting the tunnel, you'll see output like:

```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://random-name-1234.trycloudflare.com                                               |
+--------------------------------------------------------------------------------------------+
```

**Copy the HTTPS URL shown** - this is your webhook URL.

### 3. Configure GitHub Webhook

1. Go to your repository: https://github.com/amkeener/tac-5
2. Navigate to: **Settings** → **Webhooks** → **Add webhook**
3. Configure the webhook:

   **Payload URL**: `https://your-tunnel-url.trycloudflare.com/gh-webhook`
   
   **Content type**: `application/json`
   
   **Secret**: (Leave empty, or set if you want to verify webhook signatures)
   
   **Which events would you like to trigger this webhook?**:
   - ✅ Select "Let me select individual events"
   - ✅ Check "Issues"
   - ✅ Check "Issue comments"
   - ❌ Uncheck everything else
   
   **Active**: ✅ (checked)

4. Click **Add webhook**

## Webhook Details

### Endpoint Path
```
POST /gh-webhook
```

### Payload URL Format
```
https://your-tunnel-url.trycloudflare.com/gh-webhook
```

### Content Type
```
application/json
```

### Events Required
- `issues` (when opened)
- `issue_comment` (when created)

## Testing

Once configured, create a test issue with the text "adw_plan" in it:

```markdown
Please use adw_plan to create a plan for this feature
```

The webhook should trigger and you'll see:
1. A comment from the ADW bot on your issue
2. Logs in `/tmp/webhook_server.log` or the console
3. Agent execution logs in `agents/{adw_id}/`

## Troubleshooting

### Check if webhook server is running:
```bash
curl http://localhost:8001/health
```

### Check webhook server logs:
```bash
tail -f /tmp/webhook_server.log
```

### Kill existing tunnel/webhook:
```bash
./scripts/kill_trigger_webhook.sh
```

### Verify tunnel is accessible:
Replace `YOUR_URL` with your tunnel URL:
```bash
curl https://YOUR_URL.trycloudflare.com/health
```

## Important Notes

- The tunnel URL changes each time you restart (unless using a named tunnel with token)
- Keep the tunnel running while testing
- The issue/comment **must contain "adw_"** (case-insensitive) to trigger
- The webhook responds with 200 OK immediately, then processes in the background



