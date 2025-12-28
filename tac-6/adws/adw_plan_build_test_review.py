#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan, Build, Test & Review - Complete development cycle (Local-Only Mode)

Usage:
  uv run adw_plan_build_test_review.py "<description>" [adw-id]

Example:
  uv run adw_plan_build_test_review.py "Add dark mode toggle to settings page"

This script runs the complete ADW pipeline:
1. adw_plan.py - Planning phase
2. adw_build.py - Implementation phase
3. adw_test.py - Testing phase
4. adw_review.py - Review phase

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
        print('Usage: uv run adw_plan_build_test_review.py "<description>" [adw-id]')
        print("")
        print("Example:")
        print('  uv run adw_plan_build_test_review.py "Add dark mode toggle to settings page"')
        sys.exit(1)

    description = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else make_adw_id()

    print(f"ADW ID: {adw_id}")
    print(f"Description: {description}")

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
    print(f"\n=== PLAN PHASE ===")
    print(f"Running: adw_plan.py \"<description>\" {adw_id}")
    plan = subprocess.run(plan_cmd)
    if plan.returncode != 0:
        print("Plan phase failed")
        sys.exit(1)

    # Run build with ADW ID only
    build_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_build.py"),
        adw_id,
    ]
    print(f"\n=== BUILD PHASE ===")
    print(f"Running: {' '.join(build_cmd)}")
    build = subprocess.run(build_cmd)
    if build.returncode != 0:
        print("Build phase failed")
        sys.exit(1)

    # Run test with ADW ID only (skip e2e by default)
    test_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_test.py"),
        adw_id,
        "--skip-e2e",
    ]
    print(f"\n=== TEST PHASE ===")
    print(f"Running: {' '.join(test_cmd)}")
    test = subprocess.run(test_cmd)
    if test.returncode != 0:
        print("Test phase failed")
        sys.exit(1)

    # Run review with ADW ID only
    review_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_review.py"),
        adw_id,
    ]
    print(f"\n=== REVIEW PHASE ===")
    print(f"Running: {' '.join(review_cmd)}")
    review = subprocess.run(review_cmd)
    if review.returncode != 0:
        print("Review phase failed")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Plan-Build-Test-Review workflow finished successfully")
    print(f"ADW ID: {adw_id}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
