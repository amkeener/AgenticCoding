"""Local output module for ADW workflows.

This module replaces GitHub issue comments with local console + file output.
All workflow progress is logged to both stdout and the agents/{adw_id}/ directory.
"""

import os
import logging
from datetime import datetime
from typing import Optional

# Output prefix for console messages
OUTPUT_PREFIX = "[ADW]"


def log_message(
    adw_id: str,
    agent_name: str,
    message: str,
    logger: Optional[logging.Logger] = None,
) -> None:
    """Output a workflow message to console and optionally to log file.

    This replaces make_issue_comment() for local-only operation.

    Args:
        adw_id: The ADW workflow ID
        agent_name: Name of the agent (ops, planner, implementor, etc.)
        message: The message to output
        logger: Optional logger instance for file logging
    """
    formatted_msg = f"{OUTPUT_PREFIX} {adw_id}_{agent_name}: {message}"

    # Always print to console
    print(formatted_msg)

    # Also log to file if logger provided
    if logger:
        logger.info(formatted_msg)


def format_message(
    adw_id: str, agent_name: str, message: str, session_id: Optional[str] = None
) -> str:
    """Format a message for local output.

    This replaces format_issue_message() for local-only operation.

    Args:
        adw_id: The ADW workflow ID
        agent_name: Name of the agent
        message: The message content
        session_id: Optional Claude session ID

    Returns:
        Formatted message string
    """
    if session_id:
        return f"{OUTPUT_PREFIX} {adw_id}_{agent_name}_{session_id}: {message}"
    return f"{OUTPUT_PREFIX} {adw_id}_{agent_name}: {message}"


def save_summary(
    adw_id: str, content: str, filename: str = "workflow_summary.md"
) -> str:
    """Save a workflow summary to the agents directory.

    Args:
        adw_id: The ADW workflow ID
        content: Markdown content to save
        filename: Output filename (default: workflow_summary.md)

    Returns:
        Path to the saved file
    """
    # Get project root (two levels up from this file)
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    output_dir = os.path.join(project_root, "agents", adw_id)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, filename)
    with open(output_path, "w") as f:
        f.write(f"# ADW Workflow Summary: {adw_id}\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(content)

    return output_path


def log_state(adw_id: str, state_data: dict, logger: Optional[logging.Logger] = None) -> None:
    """Log the current ADW state to console.

    Args:
        adw_id: The ADW workflow ID
        state_data: Dictionary of state data
        logger: Optional logger instance
    """
    import json

    state_json = json.dumps(state_data, indent=2)
    message = f"Current state:\n```json\n{state_json}\n```"
    log_message(adw_id, "ops", message, logger)
