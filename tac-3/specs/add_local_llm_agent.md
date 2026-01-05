# Chore: Add Local LLM Agent Support

## Chore Description
Add a natural language processing agent to this project that can be used instead of the OpenAI API calls. The solution should use cursor-agent or claude CLI (both are installed) as the lightest weight approach. This will allow the application to work without requiring external API keys by leveraging local CLI-based agents.

The implementation should:
- Add support for cursor-agent and claude CLI as LLM providers
- Maintain backward compatibility with existing OpenAI and Anthropic API calls
- Use the same prompt format and SQL generation logic
- Allow configuration via environment variables or request parameters
- Be the lightest weight solution (CLI-based, no model downloads required)

## Relevant Files
Use these files to resolve the chore:

- `app/server/core/llm_processor.py` - Contains the current LLM implementation with OpenAI and Anthropic API calls. Needs to be extended with cursor-agent and claude CLI support.
- `app/server/core/data_models.py` - Contains QueryRequest model with llm_provider field. Needs to be updated to include "cursor-agent" and "claude" as valid provider options.
- `app/server/server.py` - FastAPI server that uses llm_processor. May need minor updates if provider selection logic changes.
- `app/server/tests/core/test_llm_processor.py` - Contains tests for LLM processor. Needs new tests for cursor-agent and claude CLI providers.
- `app/server/.env.sample` - Environment variable template. May need updates to document new provider options.

### New Files
- No new files required. All changes will be within existing files.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update Data Models
- Update `QueryRequest.llm_provider` field in `app/server/core/data_models.py` to include "cursor-agent" and "claude" as valid Literal options
- Change from `Literal["openai", "anthropic"]` to `Literal["openai", "anthropic", "cursor-agent", "claude"]`
- Ensure default remains "openai" for backward compatibility

### Step 2: Create CLI Agent Functions
- In `app/server/core/llm_processor.py`, create `generate_sql_with_cursor_agent()` function
  - Use subprocess to call `cursor-agent --print --force` with the prompt
  - Format the prompt using the same `format_schema_for_prompt()` function
  - Parse the response to extract SQL query (handle markdown code blocks if present)
  - Add proper error handling and timeout (60 seconds)
  - Return clean SQL string
- Create `generate_sql_with_claude()` function
  - Use subprocess to call `claude -p` with the prompt
  - Format the prompt using the same `format_schema_for_prompt()` function
  - Parse the response to extract SQL query (handle markdown code blocks if present)
  - Add proper error handling and timeout (60 seconds)
  - Return clean SQL string

### Step 3: Update Routing Logic
- Update `generate_sql()` function in `app/server/core/llm_processor.py` to handle new providers
- Add logic to check for cursor-agent availability (which cursor-agent)
- Add logic to check for claude availability (which claude)
- Update provider selection priority:
  1. If request.llm_provider is specified, use that provider
  2. If OPENAI_API_KEY exists, use OpenAI (backward compatibility)
  3. If ANTHROPIC_API_KEY exists, use Anthropic (backward compatibility)
  4. If cursor-agent is available, use cursor-agent
  5. If claude is available, use claude
  6. Otherwise, raise error with helpful message
- Maintain backward compatibility with existing behavior

### Step 4: Add Environment Variable Support
- Add optional `LLM_PROVIDER` environment variable support
- Allow setting default provider via environment variable
- Update provider selection to check `LLM_PROVIDER` env var if request doesn't specify
- Document in `.env.sample` file

### Step 5: Update Tests
- In `app/server/tests/core/test_llm_processor.py`, add tests for cursor-agent provider
  - Mock subprocess calls to cursor-agent
  - Test successful SQL generation
  - Test error handling (timeout, missing command, etc.)
- Add tests for claude provider
  - Mock subprocess calls to claude
  - Test successful SQL generation
  - Test error handling
- Add tests for provider selection logic with new providers
- Ensure all existing tests still pass

### Step 6: Update Documentation
- Update `README.md` to document new LLM provider options
- Add section explaining cursor-agent and claude CLI usage
- Update environment variable documentation
- Add troubleshooting section for CLI agent setup

### Step 7: Validation
- Run all tests to ensure zero regressions
- Test with each provider (OpenAI, Anthropic, cursor-agent, claude) if available
- Verify backward compatibility with existing API key-based providers
- Test provider fallback logic

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions
- `cd app/server && uv run pytest app/server/tests/core/test_llm_processor.py -v` - Run LLM processor tests specifically to validate new provider support
- `cd app/server && python -c "from core.llm_processor import generate_sql; from core.data_models import QueryRequest; from core.sql_processor import get_database_schema; print('Import successful')"` - Verify imports work correctly
- `which cursor-agent && echo "cursor-agent available" || echo "cursor-agent not found"` - Verify cursor-agent is available
- `which claude && echo "claude available" || echo "claude not found"` - Verify claude is available

## Notes
- Both cursor-agent and claude CLI are already installed on the system
- The lightest weight solution is to use CLI subprocess calls rather than downloading models
- cursor-agent uses `--print --force` flags for non-interactive execution
- claude uses `-p` flag for prompt input
- Both CLIs should handle the same prompt format as OpenAI/Anthropic
- Timeout of 60 seconds should be sufficient for SQL generation
- Error messages should be clear about which provider failed and why
- The solution maintains full backward compatibility with existing API-based providers




