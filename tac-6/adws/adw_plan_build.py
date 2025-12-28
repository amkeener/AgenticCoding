#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan & Build - AI Developer Workflow for agentic planning and building (Local-Only Mode)

Usage:
  uv run adw_plan_build.py "<description>" [adw-id]

Example:
  uv run adw_plan_build.py "Add dark mode toggle to settings page"

This script runs:
1. adw_plan.py - Planning phase (classifies and creates plan)
2. adw_build.py - Implementation phase (implements the plan)

All operations are local only (no push, no PR).
"""

import subprocess
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adw_modules.utils import make_adw_id


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print('Usage: uv run adw_plan_build.py "<description>" [adw-id]')
        print("")
        print("Example:")
        print('  uv run adw_plan_build.py "Add dark mode toggle to settings page"')
        sys.exit(1)

    description = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    print(f"ADW ID: {adw_id}")
    print(f"Description: {description}")
    print("")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Run plan with description
    plan_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_plan.py"),
        description,
        adw_id,
    ]
    print(f"Running: {' '.join(plan_cmd[:3])} \"<description>\" {adw_id}")
    plan = subprocess.run(plan_cmd)
    if plan.returncode != 0:
        sys.exit(1)

    # Run build with ADW ID only
    build_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_build.py"),
        adw_id,
    ]
    print(f"\nRunning: {' '.join(build_cmd)}")
    build = subprocess.run(build_cmd)
    if build.returncode != 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
