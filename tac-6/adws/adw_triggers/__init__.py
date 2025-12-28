"""
DEPRECATED: GitHub trigger scripts.

These trigger scripts are deprecated for local-only ADW operation.
The ADW system now accepts descriptions via command line:

    uv run adw_plan_build.py "Add dark mode toggle"

The code is preserved for reference and potential future GitHub integration.

Available (deprecated) triggers:
- trigger_webhook.py - GitHub webhook handler for issue events
- trigger_cron.py - GitHub polling for issue keywords
"""

import warnings

warnings.warn(
    "adw_triggers package is deprecated in local-only mode. "
    "Use command-line workflows (e.g., adw_plan_build.py) instead.",
    DeprecationWarning,
    stacklevel=2
)
