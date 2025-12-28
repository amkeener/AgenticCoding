#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan - AI Developer Workflow for agentic planning (Local-Only Mode)

Usage:
  uv run adw_plan.py "<description>" [adw-id]

Example:
  uv run adw_plan.py "Add dark mode toggle to settings page"

Workflow:
1. Create LocalIssue from description
2. Classify issue type (/chore, /bug, /feature)
3. Create feature branch
4. Generate implementation plan
5. Commit plan (local only - no push)
"""

import sys
import os
import logging
import json
from typing import Optional
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import create_branch, commit_changes, finalize_git_operations
from adw_modules.output import log_message
from adw_modules.workflow_ops import (
    classify_issue,
    build_plan,
    generate_branch_name,
    create_commit,
    AGENT_PLANNER,
)
from adw_modules.utils import setup_logger, make_adw_id
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
        print('Usage: uv run adw_plan.py "<description>" [adw-id]')
        print("")
        print("Example:")
        print('  uv run adw_plan.py "Add dark mode toggle to settings page"')
        sys.exit(1)

    description = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    # Create local issue from description
    issue = LocalIssue.from_description(description)

    # Initialize state
    state = ADWState(adw_id)
    state.update(
        adw_id=adw_id,
        description=description,
        title=issue.title,
    )
    state.save("adw_plan_init")

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_plan")
    logger.info(f"ADW Plan starting - ID: {adw_id}")
    logger.info(f"Description: {description}")

    # Validate environment
    check_env_vars(logger)

    log_message(adw_id, "ops", "Starting planning phase", logger)

    # Classify the issue
    issue_command, error = classify_issue(issue, adw_id, logger)

    if error:
        logger.error(f"Error classifying issue: {error}")
        log_message(adw_id, "ops", f"Error classifying issue: {error}", logger)
        sys.exit(1)

    state.update(issue_class=issue_command)
    state.save("adw_plan")
    logger.info(f"Issue classified as: {issue_command}")
    log_message(adw_id, "ops", f"Issue classified as: {issue_command}", logger)

    # Generate branch name
    branch_name, error = generate_branch_name(issue, issue_command, adw_id, logger)

    if error:
        logger.error(f"Error generating branch name: {error}")
        log_message(adw_id, "ops", f"Error generating branch name: {error}", logger)
        sys.exit(1)

    # Create git branch
    success, error = create_branch(branch_name)

    if not success:
        logger.error(f"Error creating branch: {error}")
        log_message(adw_id, "ops", f"Error creating branch: {error}", logger)
        sys.exit(1)

    state.update(branch_name=branch_name)
    state.save("adw_plan")
    logger.info(f"Working on branch: {branch_name}")
    log_message(adw_id, "ops", f"Working on branch: {branch_name}", logger)

    # Build the implementation plan
    logger.info("Building implementation plan")
    log_message(adw_id, AGENT_PLANNER, "Building implementation plan", logger)

    plan_response = build_plan(issue, issue_command, adw_id, logger)

    if not plan_response.success:
        logger.error(f"Error building plan: {plan_response.output}")
        log_message(adw_id, AGENT_PLANNER, f"Error building plan: {plan_response.output}", logger)
        sys.exit(1)

    logger.debug(f"Plan response: {plan_response.output}")
    log_message(adw_id, AGENT_PLANNER, "Implementation plan created", logger)

    # Get the plan file path directly from response
    logger.info("Getting plan file path")
    plan_file_path = plan_response.output.strip()

    # Validate the path exists
    if not plan_file_path:
        error = "No plan file path returned from planning agent"
        logger.error(error)
        log_message(adw_id, "ops", f"Error: {error}", logger)
        sys.exit(1)

    if not os.path.exists(plan_file_path):
        error = f"Plan file does not exist: {plan_file_path}"
        logger.error(error)
        log_message(adw_id, "ops", f"Error: {error}", logger)
        sys.exit(1)

    state.update(plan_file=plan_file_path)
    state.save("adw_plan")
    logger.info(f"Plan file created: {plan_file_path}")
    log_message(adw_id, "ops", f"Plan file created: {plan_file_path}", logger)

    # Create commit message
    logger.info("Creating plan commit")
    commit_msg, error = create_commit(
        AGENT_PLANNER, issue, issue_command, adw_id, logger
    )

    if error:
        logger.error(f"Error creating commit message: {error}")
        log_message(adw_id, AGENT_PLANNER, f"Error creating commit message: {error}", logger)
        sys.exit(1)

    # Commit the plan
    success, error = commit_changes(commit_msg)

    if not success:
        logger.error(f"Error committing plan: {error}")
        log_message(adw_id, AGENT_PLANNER, f"Error committing plan: {error}", logger)
        sys.exit(1)

    logger.info(f"Committed plan: {commit_msg}")
    log_message(adw_id, AGENT_PLANNER, "Plan committed", logger)

    # Finalize git operations (local only - no push/PR)
    finalize_git_operations(state, logger)

    logger.info("Planning phase completed successfully")
    log_message(adw_id, "ops", "Planning phase completed", logger)

    # Save final state
    state.save("adw_plan")

    # Print final state summary
    print(f"\n{'='*60}")
    print(f"ADW ID: {adw_id}")
    print(f"Branch: {branch_name}")
    print(f"Plan: {plan_file_path}")
    print(f"Classification: {issue_command}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
