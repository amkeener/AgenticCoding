#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv>=1.0.0",
#     "requests>=2.31.0",
#     "pydantic>=2.0.0",
# ]
# ///
"""Simple test script for local agent."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adw_modules.local_agent import (
    check_ollama_installed,
    check_model_available,
    run_agent_loop,
    OLLAMA_MODEL,
)


def main():
    print("=" * 60)
    print("Testing Local LLM Agent Setup")
    print("=" * 60)

    # Check Ollama
    print("\n1. Checking Ollama connection...")
    error = check_ollama_installed()
    if error:
        print(f"   ❌ {error}")
        print("\n   To fix: Make sure Ollama is running with 'ollama serve'")
        return 1
    print("   ✅ Ollama is running")

    # Check model
    print(f"\n2. Checking model '{OLLAMA_MODEL}'...")
    error = check_model_available(OLLAMA_MODEL)
    if error:
        print(f"   ⚠️  {error}")
        print(f"\n   To fix: Run 'ollama pull {OLLAMA_MODEL}'")
        # Continue anyway - we might be able to pull it
    else:
        print(f"   ✅ Model '{OLLAMA_MODEL}' is available")

    # Simple test prompt
    print("\n3. Running simple test prompt...")
    test_prompt = "What is 2 + 2? Reply with just the number."

    try:
        response, messages = run_agent_loop(test_prompt, OLLAMA_MODEL, max_iterations=3)
        print(f"   ✅ Got response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1

    # Test with tool use
    print("\n4. Testing tool use (read_file)...")
    test_prompt = "Use the read_file tool to read the README.md file and tell me what project this is."

    try:
        response, messages = run_agent_loop(test_prompt, OLLAMA_MODEL, max_iterations=5)
        print(f"   ✅ Got response: {response[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1

    print("\n" + "=" * 60)
    print("✅ All tests passed! Local agent is ready to use.")
    print("=" * 60)
    print("\nUsage:")
    print("  cd adws")
    print("  uv run adw_plan.py 'Add a dark mode toggle'")
    print("\nTo switch to Claude API (if you have credits):")
    print("  USE_LOCAL_LLM=false uv run adw_plan.py 'Add a dark mode toggle'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
