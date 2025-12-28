# Core Built-in Development Tools

## File Operations

- `read_file(targetFile: string, offset?: number, limit?: number): Promise<string>`
  - Read contents of a file from the filesystem

- `write(file_path: string, contents: string): Promise<void>`
  - Create or overwrite a file with specified contents

- `search_replace(file_path: string, old_string: string, new_string: string, replace_all?: boolean): Promise<void>`
  - Replace text in a file (supports single or all occurrences)

- `delete_file(target_file: string): Promise<void>`
  - Delete a file from the filesystem

- `list_dir(target_directory: string, ignore_globs?: string[]): Promise<DirectoryListing>`
  - List files and directories in a given path

- `glob_file_search(glob_pattern: string, target_directory?: string): Promise<string[]>`
  - Search for files matching a glob pattern

## Code Search & Navigation

- `codebase_search(query: string, target_directories?: string[], search_only_prs?: boolean): Promise<SearchResults>`
  - Semantic search across the codebase using natural language queries

- `grep(pattern: string, path?: string, type?: string, output_mode?: "content" | "files_with_matches" | "count", -B?: number, -A?: number, -C?: number, -i?: boolean, multiline?: boolean, head_limit?: number): Promise<GrepResults>`
  - Powerful regex-based search using ripgrep

## Terminal & Command Execution

- `run_terminal_cmd(command: string, is_background?: boolean, required_permissions?: ("git_write" | "network" | "all")[]): Promise<CommandResult>`
  - Execute shell commands with optional permissions and background execution

## Code Quality

- `read_lints(paths?: string[]): Promise<LintDiagnostics>`
  - Read linter errors and warnings for specified files or directories

## Notebook Support

- `edit_notebook(target_notebook: string, cell_idx: number, is_new_cell: boolean, cell_language: string, old_string: string, new_string: string): Promise<void>`
  - Edit or create cells in Jupyter notebooks

## Task Management

- `todo_write(merge: boolean, todos: TodoItem[]): Promise<void>`
  - Create and manage structured task lists

## Web Search

- `web_search(search_term: string): Promise<SearchResults>`
  - Search the web for real-time information

---

# Cursor-Agent CLI Tools

When running `cursor-agent`, the AI agent has access to the following tools:

## File Operations (via cursor-agent)

- `write(file: string, content: string): Promise<void>`
  - Write/create files in the workspace
  - Access provided when using `--print` flag

## Command Execution (via cursor-agent)

- `bash(command: string, options?: BashOptions): Promise<CommandResult>`
  - Execute bash/shell commands
  - Requires `--force` flag for automated execution in non-interactive mode
  - Access provided when using `--print` flag

## Cursor-Agent CLI Options

- `cursor-agent --print [prompt]`
  - Enable non-interactive mode with access to write and bash tools
  
- `cursor-agent --force`
  - Force allow commands unless explicitly denied
  
- `cursor-agent --output-format <text|json|stream-json>`
  - Control output format for programmatic use
  
- `cursor-agent --stream-partial-output`
  - Stream partial output as text deltas (requires stream-json format)
  
- `cursor-agent --browser`
  - Enable browser automation support
  
- `cursor-agent --workspace <path>`
  - Set workspace directory (defaults to current working directory)
  
- `cursor-agent --model <model>`
  - Specify AI model (e.g., gpt-5, sonnet-4, sonnet-4-thinking)
  
- `cursor-agent --approve-mcps`
  - Automatically approve all MCP servers (headless mode only)

## Cursor-Agent Commands

- `cursor-agent login`
  - Authenticate with Cursor (required before use)

- `cursor-agent logout`
  - Sign out and clear authentication

- `cursor-agent status|whoami`
  - View authentication status

- `cursor-agent update|upgrade`
  - Update to latest version

- `cursor-agent create-chat`
  - Create new empty chat and return chat ID

- `cursor-agent resume [chatId]`
  - Resume a chat session

- `cursor-agent mcp`
  - Manage MCP servers

- `cursor-agent install-shell-integration`
  - Install shell integration to ~/.zshrc

- `cursor-agent uninstall-shell-integration`
  - Remove shell integration

