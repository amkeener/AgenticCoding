#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Build - AI Developer Workflow for agentic building (Local-Only Mode)

Usage:
  uv run adw_build.py <adw-id>

The adw-id is required to locate the plan file created by adw_plan.py.

Workflow:
1. Find existing plan (from state)
2. Implement the solution based on plan
3. Commit implementation (local only - no push)
"""

import sys
import os
import logging
import subprocess
from typing import Optional
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations
from adw_modules.output import log_message
from adw_modules.workflow_ops import (
    implement_plan,
    create_commit,
    classify_issue,
    AGENT_IMPLEMENTOR,
)
from adw_modules.utils import setup_logger
from adw_modules.data_types import LocalIssue


def check_env_vars(logger: Optional[logging.Logger] = None) -> None:
    """Check that all required environment variables are set."""
    required_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_PATH",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = "Error: Missing required environment variables:"
        if logger:
            logger.error(error_msg)
            for var in missing_vars:
                logger.error(f"  - {var}")
        else:
            print(error_msg, file=sys.stderr)
            for var in missing_vars:
                print(f"  - {var}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_build.py <adw-id>")
        print("\nError: adw-id is required to locate the plan file created by adw_plan.py")
        sys.exit(1)

    adw_id = sys.argv[1]

    # Try to load existing state
    temp_logger = setup_logger(adw_id, "adw_build")
    state = ADWState.load(adw_id, temp_logger)
    if not state:
        # No existing state found
        logger = setup_logger(adw_id, "adw_build")
        logger.error(f"No state found for ADW ID: {adw_id}")
        logger.error("Run adw_plan.py first to create the plan and state")
        print(f"\nError: No state found for ADW ID: {adw_id}")
        print("Run adw_plan.py first to create the plan and state")
        sys.exit(1)

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_build")
    logger.info(f"ADW Build starting - ID: {adw_id}")

    log_message(adw_id, "ops", "Found existing state - resuming build", logger)

    # Validate environment
    check_env_vars(logger)

    # Ensure we have required state fields
    if not state.get("branch_name"):
        error_msg = "No branch name in state - run adw_plan.py first"
        logger.error(error_msg)
        log_message(adw_id, "ops", f"Error: {error_msg}", logger)
        sys.exit(1)

    if not state.get("plan_file"):
        error_msg = "No plan file in state - run adw_plan.py first"
        logger.error(error_msg)
        log_message(adw_id, "ops", f"Error: {error_msg}", logger)
        sys.exit(1)

    # Checkout the branch from state
    branch_name = state.get("branch_name")
    result = subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Failed to checkout branch {branch_name}: {result.stderr}")
        log_message(adw_id, "ops", f"Error: Failed to checkout branch {branch_name}", logger)
        sys.exit(1)
    logger.info(f"Checked out branch: {branch_name}")

    # Get the plan file from state
    plan_file = state.get("plan_file")
    logger.info(f"Using plan file: {plan_file}")

    log_message(adw_id, "ops", "Starting implementation phase", logger)

    # Implement the plan
    logger.info("Implementing solution")
    log_message(adw_id, AGENT_IMPLEMENTOR, "Implementing solution", logger)

    implement_response = implement_plan(plan_file, adw_id, logger)

    if not implement_response.success:
        logger.error(f"Error implementing solution: {implement_response.output}")
        log_message(adw_id, AGENT_IMPLEMENTOR, f"Error: {implement_response.output}", logger)
        sys.exit(1)

    logger.debug(f"Implementation response: {implement_response.output}")
    log_message(adw_id, AGENT_IMPLEMENTOR, "Solution implemented", logger)

    # Create LocalIssue from state description for commit message
    description = state.get("description") or state.get("title") or "Local implementation"
    issue = LocalIssue.from_description(description)

    # Get issue classification from state or classify if needed
    issue_command = state.get("issue_class")
    if not issue_command:
        logger.info("No issue classification in state, running classify_issue")
        issue_command, error = classify_issue(issue, adw_id, logger)
        if error:
            logger.error(f"Error classifying issue: {error}")
            # Default to feature if classification fails
            issue_command = "/feature"
            logger.warning("Defaulting to /feature after classification error")
        else:
            # Save the classification for future use
            state.update(issue_class=issue_command)
            state.save("adw_build")

    # Create commit message
    logger.info("Creating implementation commit")
    commit_msg, error = create_commit(AGENT_IMPLEMENTOR, issue, issue_command, adw_id, logger)

    if error:
        logger.error(f"Error creating commit message: {error}")
        log_message(adw_id, AGENT_IMPLEMENTOR, f"Error: {error}", logger)
        sys.exit(1)

    # Commit the implementation
    success, error = commit_changes(commit_msg)

    if not success:
        logger.error(f"Error committing implementation: {error}")
        log_message(adw_id, AGENT_IMPLEMENTOR, f"Error: {error}", logger)
        sys.exit(1)

    logger.info(f"Committed implementation: {commit_msg}")
    log_message(adw_id, AGENT_IMPLEMENTOR, "Implementation committed", logger)

    # Finalize git operations (local only - no push/PR)
    finalize_git_operations(state, logger)

    logger.info("Implementation phase completed successfully")
    log_message(adw_id, "ops", "Implementation phase completed", logger)

    # Save final state
    state.save("adw_build")

    # Print final summary
    print(f"\n{'='*60}")
    print(f"ADW ID: {adw_id}")
    print(f"Branch: {branch_name}")
    print(f"Plan: {plan_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
