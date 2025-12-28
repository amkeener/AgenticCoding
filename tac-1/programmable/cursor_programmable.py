import subprocess
import sys


def main():
    with open("programmable/prompt.md", "r") as f:
        prompt_content = f.read()

    # cursor-agent --print enables print mode (non-interactive)
    # --force flag allows commands unless explicitly denied
    # Pass prompt as arguments - subprocess will handle multi-line content
    command = [
        "cursor-agent",
        "--print",
        "--force",  # Force allow commands (like terminal commands)
        prompt_content,
    ]

    try:
        # Add timeout to prevent hanging (60 seconds should be enough)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print("Error: cursor-agent command timed out after 60 seconds.", file=sys.stderr)
        print("The agent may be waiting for input or taking longer than expected.", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: cursor-agent not found. Please install it first:", file=sys.stderr)
        print("  curl https://cursor.com/install -fsS | bash", file=sys.stderr)
        print("\nThen run 'cursor-agent login' to authenticate.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
