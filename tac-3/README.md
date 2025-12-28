# Natural Language SQL Interface

A web application that converts natural language queries to SQL using AI, built with FastAPI and Vite + TypeScript.

## Features

- 🗣️ Natural language to SQL conversion using OpenAI, Anthropic, cursor-agent, or claude CLI
- 📁 Drag-and-drop file upload (.csv and .json)
- 📊 Interactive table results display
- 🔒 SQL injection protection
- ⚡ Fast development with Vite and uv
- 🚀 Local LLM support via CLI agents (no API keys required)

## Prerequisites

- Python 3.10+
- Node.js 18+
- One of the following:
  - OpenAI API key and/or Anthropic API key, OR
  - cursor-agent CLI installed (`curl https://cursor.com/install -fsS | bash`), OR
  - claude CLI installed

## Setup

### 1. Install Dependencies

```bash
# Backend
cd app/server
uv sync --all-extras

# Frontend
cd app/client
npm install
```

### 2. Environment Configuration

Set up your API keys or LLM provider in the root and the server directory:

```bash
cp .env.sample .env
```

and

```bash
cd app/server
cp .env.sample .env
# Edit .env and add your API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)
# OR set LLM_PROVIDER=cursor-agent or LLM_PROVIDER=claude to use CLI agents
```

**LLM Provider Options:**
- `OPENAI_API_KEY` - Use OpenAI API (requires API key)
- `ANTHROPIC_API_KEY` - Use Anthropic API (requires API key)
- `LLM_PROVIDER=cursor-agent` - Use cursor-agent CLI (no API key needed)
- `LLM_PROVIDER=claude` - Use claude CLI (no API key needed)

If no API keys are set, the system will automatically fall back to cursor-agent or claude CLI if available.


## Quick Start

Use the provided script to start both services:

```bash
./scripts/start.sh
```

Or use the fresh start script to kill any existing instances and start fresh:

```bash
./scripts/fresh_start.sh
```

Press `Ctrl+C` to stop both services.

The scripts will:
- Check that `.env` exists in `app/server/`
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:5173
- Handle graceful shutdown when you exit

**Note:** `fresh_start.sh` will kill any existing server instances on ports 8000 and 5173 before starting, ensuring a clean restart.

## Manual Start (Alternative)

### Backend
```bash
cd app/server
# .env is loaded automatically by python-dotenv
uv run python server.py
```

### Frontend
```bash
cd app/client
npm run dev
```

## Usage

1. **Upload Data**: Click "Upload Data" to open the modal
   - Use sample data buttons for quick testing
   - Or drag and drop your own .csv or .json files
   - Uploading a file with the same name will overwrite the existing table
2. **Query Your Data**: Type a natural language query like "Show me all users who signed up last week"
   - Press `Cmd+Enter` (Mac) or `Ctrl+Enter` (Windows/Linux) to run the query
3. **View Results**: See the generated SQL and results in a table format
4. **Manage Tables**: Click the × button on any table to remove it

## Development

### Backend Commands
```bash
cd app/server
uv run python server.py      # Start server with hot reload
uv run pytest               # Run tests
uv add <package>            # Add package to project
uv remove <package>         # Remove package from project
uv sync --all-extras        # Sync all extras
```

### Frontend Commands
```bash
cd app/client
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build
```

## Project Structure

```
app/
├── client/                 # Vite + TypeScript frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── types.d.ts     # TypeScript types
│   │   └── main.ts        # App entry point
│   └── vite.config.ts     # Vite configuration
│
└── server/                # FastAPI backend
    ├── core/              # Core modules
    │   ├── data_models.py # Pydantic models
    │   ├── file_processor.py
    │   ├── llm_processor.py
    │   ├── sql_processor.py
    │   └── insights.py
    ├── db/                # SQLite database
    └── server.py          # FastAPI app
```

## API Endpoints

- `POST /api/upload` - Upload CSV/JSON file
- `POST /api/query` - Process natural language query
- `GET /api/schema` - Get database schema
- `POST /api/insights` - Generate column insights
- `GET /api/health` - Health check

## Security

- Only SELECT queries are allowed
- SQL injection protection via keyword blocking
- File upload validation
- CORS configured for local development

## LLM Provider Configuration

The application supports multiple LLM providers:

1. **OpenAI API** (default if API key is set)
   - Set `OPENAI_API_KEY` in `.env`
   - Requires paid OpenAI API access

2. **Anthropic API**
   - Set `ANTHROPIC_API_KEY` in `.env`
   - Requires paid Anthropic API access

3. **cursor-agent CLI** (lightweight, no API key needed)
   - Install: `curl https://cursor.com/install -fsS | bash`
   - Authenticate: `cursor-agent login`
   - Set `LLM_PROVIDER=cursor-agent` in `.env` or use in request

4. **claude CLI** (lightweight, no API key needed)
   - Install: Check Claude Desktop documentation
   - Set `LLM_PROVIDER=claude` in `.env` or use in request

**Provider Selection Priority:**
1. Request `llm_provider` parameter (if specified)
2. `LLM_PROVIDER` environment variable
3. `OPENAI_API_KEY` (if set)
4. `ANTHROPIC_API_KEY` (if set)
5. cursor-agent CLI (if available)
6. claude CLI (if available)

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (requires 3.12+)
- Verify API keys or CLI agents are available: `echo $OPENAI_API_KEY` or `which cursor-agent`

**LLM provider errors:**
- For CLI agents: Ensure cursor-agent or claude is installed and in PATH
- For API providers: Verify API keys are set correctly
- Check provider availability: `which cursor-agent` or `which claude`

**Frontend errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (requires 18+)

**CORS issues:**
- Ensure backend is running on port 8000
- Check vite.config.ts proxy settings