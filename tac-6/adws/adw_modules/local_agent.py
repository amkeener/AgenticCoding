"""Local LLM agent module using Ollama for executing prompts without API costs."""

import subprocess
import sys
import os
import json
import re
import glob as glob_module
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Final
from dotenv import load_dotenv
import requests

from .data_types import (
    AgentPromptRequest,
    AgentPromptResponse,
    AgentTemplateRequest,
    SlashCommand,
)

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")

# Model mapping for different task complexities
# Maps original Claude model names to local equivalents
# Override with OLLAMA_MODEL_LARGE and OLLAMA_MODEL_SMALL env vars
MODEL_MAP: Final[Dict[str, str]] = {
    "opus": os.getenv("OLLAMA_MODEL_LARGE", "deepseek-r1:14b"),    # Complex tasks: /feature, /bug, /implement, /review
    "sonnet": os.getenv("OLLAMA_MODEL_SMALL", "deepseek-r1:8b"),  # Simple tasks: /classify_issue, /commit, etc.
}

# Flag to enable/disable local mode (set via USE_LOCAL_LLM env var or --local flag)
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() in ("true", "1", "yes")

# Tool definitions for the agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file at the given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating it if it doesn't exist",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write to"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace a specific string in a file with new content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to edit"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "The exact string to find and replace"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "The string to replace it with"
                    }
                },
                "required": ["path", "old_string", "new_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a bash command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "glob_search",
            "description": "Find files matching a glob pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The glob pattern to match (e.g., '**/*.py')"
                    },
                    "path": {
                        "type": "string",
                        "description": "The directory to search in (default: current directory)"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for a pattern in files using regex",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The regex pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "The file or directory to search in"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Optional glob pattern to filter files (e.g., '*.py')"
                    }
                },
                "required": ["pattern"]
            }
        }
    }
]


def get_project_root() -> str:
    """Get the project root directory (parent of adws)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_ollama_installed() -> Optional[str]:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code != 200:
            return f"Error: Ollama is not responding at {OLLAMA_HOST}"
        return None
    except requests.exceptions.ConnectionError:
        return f"Error: Cannot connect to Ollama at {OLLAMA_HOST}. Is Ollama running?"
    except Exception as e:
        return f"Error checking Ollama: {e}"


def check_model_available(model: str) -> Optional[str]:
    """Check if the specified model is available in Ollama."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            model_base = model.split(":")[0]
            if model_base not in model_names and model not in [m.get("name") for m in models]:
                return f"Model '{model}' not found. Available: {', '.join(m.get('name') for m in models)}"
        return None
    except Exception as e:
        return f"Error checking model: {e}"


# Tool implementations
def tool_read_file(path: str) -> str:
    """Read a file and return its contents."""
    try:
        # Handle relative paths from project root
        if not os.path.isabs(path):
            path = os.path.join(get_project_root(), path)

        with open(path, "r") as f:
            content = f.read()
        return f"File contents of {path}:\n```\n{content}\n```"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def tool_write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        # Handle relative paths from project root
        if not os.path.isabs(path):
            path = os.path.join(get_project_root(), path)

        # Create parent directories if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def tool_edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace a string in a file."""
    try:
        # Handle relative paths from project root
        if not os.path.isabs(path):
            path = os.path.join(get_project_root(), path)

        with open(path, "r") as f:
            content = f.read()

        if old_string not in content:
            return f"Error: String not found in {path}"

        # Check for uniqueness
        count = content.count(old_string)
        if count > 1:
            return f"Error: String appears {count} times in {path}. Provide more context for unique match."

        new_content = content.replace(old_string, new_string)

        with open(path, "w") as f:
            f.write(new_content)

        return f"Successfully edited {path}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except Exception as e:
        return f"Error editing file: {e}"


def tool_bash(command: str) -> str:
    """Execute a bash command."""
    # Security: Block dangerous commands
    dangerous_patterns = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r">\s*/dev/sd",
        r"mkfs\.",
        r"dd\s+if=",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return f"Error: Command blocked for safety: {command}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=get_project_root()
        )

        output = ""
        if result.stdout:
            output += f"stdout:\n{result.stdout}\n"
        if result.stderr:
            output += f"stderr:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Exit code: {result.returncode}"

        return output if output else "Command completed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 120 seconds"
    except Exception as e:
        return f"Error executing command: {e}"


def tool_glob_search(pattern: str, path: str = None) -> str:
    """Find files matching a glob pattern."""
    try:
        search_path = path or get_project_root()
        if not os.path.isabs(search_path):
            search_path = os.path.join(get_project_root(), search_path)

        full_pattern = os.path.join(search_path, pattern)
        matches = glob_module.glob(full_pattern, recursive=True)

        # Make paths relative to project root
        project_root = get_project_root()
        relative_matches = [os.path.relpath(m, project_root) for m in matches]

        if not relative_matches:
            return f"No files found matching pattern: {pattern}"

        return f"Found {len(relative_matches)} files:\n" + "\n".join(relative_matches[:50])
    except Exception as e:
        return f"Error in glob search: {e}"


def tool_grep_search(pattern: str, path: str = None, file_pattern: str = None) -> str:
    """Search for a pattern in files."""
    try:
        search_path = path or get_project_root()
        if not os.path.isabs(search_path):
            search_path = os.path.join(get_project_root(), search_path)

        # Build grep command
        cmd = ["grep", "-rn", "--include=" + (file_pattern or "*"), pattern, search_path]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.stdout:
            lines = result.stdout.strip().split("\n")
            return f"Found {len(lines)} matches:\n" + "\n".join(lines[:30])
        else:
            return f"No matches found for pattern: {pattern}"
    except subprocess.TimeoutExpired:
        return "Error: Search timed out"
    except Exception as e:
        return f"Error in grep search: {e}"


def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with given arguments."""
    tool_functions = {
        "read_file": lambda args: tool_read_file(args["path"]),
        "write_file": lambda args: tool_write_file(args["path"], args["content"]),
        "edit_file": lambda args: tool_edit_file(args["path"], args["old_string"], args["new_string"]),
        "bash": lambda args: tool_bash(args["command"]),
        "glob_search": lambda args: tool_glob_search(args["pattern"], args.get("path")),
        "grep_search": lambda args: tool_grep_search(args["pattern"], args.get("path"), args.get("file_pattern")),
    }

    if name not in tool_functions:
        return f"Error: Unknown tool '{name}'"

    return tool_functions[name](arguments)


def load_slash_command(slash_command: str) -> Optional[str]:
    """Load a slash command template from .claude/commands/."""
    command_name = slash_command.lstrip("/")
    command_path = os.path.join(get_project_root(), ".claude", "commands", f"{command_name}.md")

    if os.path.exists(command_path):
        with open(command_path, "r") as f:
            return f.read()
    return None


def expand_template(template: str, args: List[str]) -> str:
    """Expand a slash command template with arguments."""
    # Replace $ARGUMENTS with all args joined
    result = template.replace("$ARGUMENTS", " ".join(args))

    # Replace positional args $1, $2, $3, etc.
    for i, arg in enumerate(args, 1):
        result = result.replace(f"${i}", arg)

    return result


def chat_with_ollama(
    messages: List[Dict[str, Any]],
    model: str,
    tools: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """Send a chat request to Ollama and return the response."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    # Don't pass tools - we'll use prompt-based tool calling for compatibility
    # if tools:
    #     payload["tools"] = tools

    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        timeout=300  # 5 minute timeout for generation
    )

    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

    return response.json()


def parse_tool_calls_from_text(text: str) -> List[Dict[str, Any]]:
    """Parse tool calls from model output text.

    Looks for JSON blocks with tool calls in format:
    ```tool
    {"name": "tool_name", "arguments": {...}}
    ```
    or
    <tool_call>{"name": "tool_name", "arguments": {...}}</tool_call>
    """
    tool_calls = []

    # Pattern 1: ```tool ... ``` blocks
    tool_block_pattern = r'```tool\s*\n?(.*?)\n?```'
    matches = re.findall(tool_block_pattern, text, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match.strip())
            tool_calls.append(data)
        except json.JSONDecodeError:
            continue

    # Pattern 2: <tool_call>...</tool_call> tags
    tag_pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    matches = re.findall(tag_pattern, text, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match.strip())
            tool_calls.append(data)
        except json.JSONDecodeError:
            continue

    # Pattern 3: Look for JSON objects with "name" and "arguments" keys
    json_pattern = r'\{[^{}]*"name"\s*:\s*"[^"]+"\s*,[^{}]*"arguments"\s*:\s*\{[^{}]*\}[^{}]*\}'
    matches = re.findall(json_pattern, text)
    for match in matches:
        try:
            data = json.loads(match)
            if "name" in data and "arguments" in data:
                if data not in tool_calls:  # Avoid duplicates
                    tool_calls.append(data)
        except json.JSONDecodeError:
            continue

    return tool_calls


def run_agent_loop(
    prompt: str,
    model: str,
    max_iterations: int = 20
) -> Tuple[str, List[Dict[str, Any]]]:
    """Run the agent loop with prompt-based tool calling until completion."""

    system_prompt = """You are a helpful AI coding assistant. You have access to tools to help you complete tasks.

## Available Tools

1. **read_file** - Read file contents
   Arguments: {"path": "file/path"}

2. **write_file** - Write content to a file
   Arguments: {"path": "file/path", "content": "file content"}

3. **edit_file** - Replace a specific string in a file
   Arguments: {"path": "file/path", "old_string": "text to find", "new_string": "replacement text"}

4. **bash** - Execute shell commands
   Arguments: {"command": "shell command"}

5. **glob_search** - Find files matching patterns
   Arguments: {"pattern": "**/*.py", "path": "optional/directory"}

6. **grep_search** - Search for patterns in files
   Arguments: {"pattern": "regex pattern", "path": "optional/directory", "file_pattern": "*.py"}

## How to Call Tools

To use a tool, include a tool call block in your response:

```tool
{"name": "tool_name", "arguments": {"arg1": "value1"}}
```

Example:
```tool
{"name": "read_file", "arguments": {"path": "README.md"}}
```

## Important Rules

1. Call ONE tool at a time and wait for the result before calling another
2. After receiving tool results, analyze them and decide next steps
3. When your task is complete, provide a clear final answer WITHOUT any tool blocks
4. Think step by step about what you need to do

Begin by analyzing the task and determining what information you need."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    all_messages = []
    final_response = ""

    for iteration in range(max_iterations):
        print(f"  [Agent loop iteration {iteration + 1}/{max_iterations}]", file=sys.stderr)

        try:
            response = chat_with_ollama(messages, model)
        except Exception as e:
            return f"Error in agent loop: {e}", all_messages

        message = response.get("message", {})
        content = message.get("content", "")
        all_messages.append(message)

        # Parse tool calls from the text
        tool_calls = parse_tool_calls_from_text(content)

        if not tool_calls:
            # No tool calls found - agent is done
            final_response = content
            break

        # Add assistant message to history
        messages.append({"role": "assistant", "content": content})

        # Process each tool call
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("arguments", {})

            print(f"  [Tool: {tool_name}]", file=sys.stderr)

            tool_result = execute_tool(tool_name, tool_args)
            tool_results.append(f"**{tool_name}** result:\n{tool_result}")

            all_messages.append({
                "role": "tool",
                "name": tool_name,
                "content": tool_result
            })

        # Add tool results as user message (since we're not using native tool calling)
        results_message = "\n\n".join(tool_results)
        messages.append({
            "role": "user",
            "content": f"Tool results:\n\n{results_message}\n\nContinue with your task. If complete, provide your final answer without tool blocks."
        })

    return final_response, all_messages


def save_prompt(prompt: str, adw_id: str, agent_name: str = "ops") -> None:
    """Save a prompt to the appropriate logging directory."""
    match = re.match(r"^(/\w+)", prompt)
    if not match:
        return

    slash_command = match.group(1)
    command_name = slash_command[1:]

    project_root = get_project_root()
    prompt_dir = os.path.join(project_root, "agents", adw_id, agent_name, "prompts")
    os.makedirs(prompt_dir, exist_ok=True)

    prompt_file = os.path.join(prompt_dir, f"{command_name}.txt")
    with open(prompt_file, "w") as f:
        f.write(prompt)

    print(f"Saved prompt to: {prompt_file}")


def save_output(messages: List[Dict], output_file: str) -> None:
    """Save agent output to files."""
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save as JSONL
    with open(output_file, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    # Save as JSON
    json_file = output_file.replace(".jsonl", ".json")
    with open(json_file, "w") as f:
        json.dump(messages, f, indent=2)

    print(f"Output saved to: {output_file}")


def prompt_local_agent(request: AgentPromptRequest) -> AgentPromptResponse:
    """Execute a prompt using the local Ollama agent."""

    # Check if Ollama is running
    error_msg = check_ollama_installed()
    if error_msg:
        return AgentPromptResponse(output=error_msg, success=False, session_id=None)

    # Map model names
    model = MODEL_MAP.get(request.model, OLLAMA_MODEL)

    # Check if model is available
    error_msg = check_model_available(model)
    if error_msg:
        print(f"Warning: {error_msg}", file=sys.stderr)
        # Try to pull the model
        print(f"Attempting to pull model {model}...", file=sys.stderr)
        try:
            subprocess.run(["ollama", "pull", model], check=True)
        except Exception as e:
            return AgentPromptResponse(
                output=f"Model not available and pull failed: {e}",
                success=False,
                session_id=None
            )

    # Save prompt before execution
    save_prompt(request.prompt, request.adw_id, request.agent_name)

    print(f"Running local agent with model: {model}", file=sys.stderr)

    try:
        # Run the agent loop
        final_response, all_messages = run_agent_loop(request.prompt, model)

        # Save output
        save_output(all_messages, request.output_file)

        return AgentPromptResponse(
            output=final_response,
            success=True,
            session_id=request.adw_id  # Use adw_id as session identifier
        )

    except Exception as e:
        error_msg = f"Error executing local agent: {e}"
        print(error_msg, file=sys.stderr)
        return AgentPromptResponse(output=error_msg, success=False, session_id=None)


def execute_template(request: AgentTemplateRequest) -> AgentPromptResponse:
    """Execute a slash command template with the local agent."""

    # Load the slash command template
    template = load_slash_command(request.slash_command)

    if template:
        # Expand template with arguments
        prompt = expand_template(template, request.args)
    else:
        # No template found, use raw slash command format
        prompt = f"{request.slash_command} {' '.join(request.args)}"

    # Create output directory
    project_root = get_project_root()
    output_dir = os.path.join(project_root, "agents", request.adw_id, request.agent_name)
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "raw_output.jsonl")

    # Create prompt request
    prompt_request = AgentPromptRequest(
        prompt=prompt,
        adw_id=request.adw_id,
        agent_name=request.agent_name,
        model=request.model,
        dangerously_skip_permissions=True,
        output_file=output_file,
    )

    return prompt_local_agent(prompt_request)


# Compatibility aliases for drop-in replacement
prompt_claude_code = prompt_local_agent
