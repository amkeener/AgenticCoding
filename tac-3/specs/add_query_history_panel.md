# Feature: Query History Side Panel

## Research Summary

**Key Architectural Patterns Discovered:**
- FastAPI backend with RESTful API endpoints using Pydantic models for type safety
- TypeScript frontend with vanilla JS (no framework), using global state variables
- SQLite database stored in `db/database.db` with dynamic table creation
- API client pattern: centralized `apiRequest` function in `client.ts` with typed methods
- Modal system exists using fixed positioning with overlay (z-index: 1000)
- CSS variables for theming (`--primary-color`, `--surface`, etc.)
- LLM integration supports multiple providers (OpenAI, Anthropic, cursor-agent, claude CLI) via routing in `llm_processor.py`

**Similar Features and Implementation Patterns:**
- **Upload Modal**: Uses fixed positioning, overlay background, close button pattern - can be adapted for side panel
- **Results Display**: Uses `displayResults()` function that populates DOM elements - similar pattern needed for history items
- **Table Display**: Uses `displayTables()` with dynamic DOM creation - similar pattern for query list
- **API Endpoints**: Follow pattern of POST/GET with Request/Response models in `data_models.py`

**Integration Points Identified:**
- `/api/query` endpoint in `server.py` - needs to save query to history after successful execution
- `displayResults()` in `main.ts` - needs to trigger history save
- `api.processQuery()` in `client.ts` - returns QueryResponse that contains all data needed for history
- Query input section in `index.html` - where "Show Panel" button will be added

**Files That Will Be Affected:**
- Backend: `server.py`, `core/data_models.py`, `core/llm_processor.py` (new function), new `core/query_history.py`
- Frontend: `index.html`, `src/main.ts`, `src/api/client.ts`, `src/style.css`, `src/types.d.ts`

**Dependencies and Libraries:**
- No new libraries needed - SQLite is built-in, JSON serialization built-in
- Existing LLM providers will be used for generating display names

## Feature Description

A query history side panel that displays all completed queries in a scrollable list, ordered by newest first. Each query entry shows an LLM-generated display name for easy identification. Clicking a query entry refocuses the main panel to show that query's results. The panel can be toggled via a "Show Panel" button next to the "Upload Data" button. All queries are persisted in the database for persistence across sessions.

## User Story

As a user of the Natural Language SQL Interface
I want to view and access my previous queries in a side panel
So that I can quickly revisit past queries and their results without retyping them

## Problem Statement

Currently, users have no way to access their previous queries after they've been executed. If a user wants to revisit a query, they must remember and retype it. This creates friction and reduces productivity, especially when working with complex queries or when iterating on similar queries.

## Solution Statement

Implement a persistent query history system with:
1. **Database Storage**: Create a `query_history` table to store completed queries with their SQL, results, and metadata
2. **LLM-Generated Names**: Use the existing LLM infrastructure to generate concise, descriptive names for each query
3. **Side Panel UI**: Create a slide-in side panel (similar to modal pattern but from the right side) that displays query history
4. **Query Refocusing**: When clicking a history item, restore the query text to the input and display the results
5. **Toggle Button**: Add a "Show Panel" button next to "Upload Data" to open/close the panel

## Relevant Files

Use these files to implement the feature:

### Backend Files
- `app/server/server.py` - Add query history endpoints and modify `/api/query` to save history
- `app/server/core/data_models.py` - Add QueryHistoryItem, QueryHistoryResponse, QueryHistoryDetailResponse models
- `app/server/core/llm_processor.py` - Add `generate_query_display_name()` function for LLM name generation
- `app/server/core/sql_processor.py` - Reference for database connection patterns
- `app/server/core/query_history.py` - **NEW FILE** - Database operations for query history (save, retrieve, initialize table)

### Frontend Files
- `app/client/index.html` - Add side panel HTML structure and "Show Panel" button
- `app/client/src/main.ts` - Add panel toggle logic, history loading, and query refocus functionality
- `app/client/src/api/client.ts` - Add `getQueryHistory()` and `getQueryHistoryById()` methods
- `app/client/src/style.css` - Add side panel styling (slide-in animation, positioning)
- `app/client/src/types.d.ts` - Add TypeScript interfaces for query history types

## Implementation Plan

### Phase 1: Foundation
1. Create database schema for `query_history` table
2. Add Pydantic models for query history (Request/Response types)
3. Add TypeScript type definitions matching Pydantic models
4. Create `query_history.py` module with database operations
5. Add LLM function to generate display names

### Phase 2: Core Implementation
1. Modify `/api/query` endpoint to save successful queries to history
2. Add `/api/query-history` GET endpoint to retrieve all queries (newest first)
3. Add `/api/query-history/{id}` GET endpoint to retrieve specific query details
4. Update API client with history methods
5. Add side panel HTML structure
6. Add side panel CSS styling with slide-in animation
7. Implement panel toggle functionality
8. Implement history loading and display
9. Implement query refocusing on click

### Phase 3: Integration
1. Add "Show Panel" button next to "Upload Data" button
2. Ensure history updates after each successful query
3. Test persistence across page refreshes
4. Handle edge cases (empty history, failed queries, etc.)

## Step by Step Tasks

### Step 1: Database Schema and Models
- Create `query_history` table schema in `core/query_history.py` with columns:
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `query_text` (TEXT NOT NULL) - original natural language query
  - `sql` (TEXT NOT NULL) - generated SQL query
  - `display_name` (TEXT NOT NULL) - LLM-generated name
  - `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  - `results` (TEXT) - JSON string of query results
  - `columns` (TEXT) - JSON string of column names
  - `row_count` (INTEGER DEFAULT 0)
  - `execution_time_ms` (REAL DEFAULT 0)
- Add index on `created_at DESC` for efficient ordering
- Add `init_query_history_table()` function to create table on startup

### Step 2: Data Models
- Add `QueryHistoryItem` model to `data_models.py`:
  - id, query_text, sql, display_name, created_at, row_count, execution_time_ms
- Add `QueryHistoryResponse` model:
  - queries: List[QueryHistoryItem], total: int, error: Optional[str]
- Add `QueryHistoryDetailResponse` model:
  - All fields from QueryHistoryItem plus results, columns
- Add corresponding TypeScript interfaces to `types.d.ts`

### Step 3: LLM Display Name Generation
- Add `generate_query_display_name(query_text: str, sql: str) -> str` function to `llm_processor.py`
- Use existing LLM routing logic (same provider selection as SQL generation)
- Prompt: "Generate a concise, descriptive name (max 50 chars) for this query: '{query_text}' with SQL: '{sql}'. Return only the name, no quotes or explanations."
- Handle errors gracefully (fallback to truncated query_text if LLM fails)

### Step 4: Query History Database Module
- Create `core/query_history.py` with functions:
  - `init_query_history_table()` - Initialize table on app startup
  - `save_query_history(query_text, sql, results, columns, row_count, execution_time_ms) -> int` - Save query and return ID
  - `get_all_query_history() -> List[QueryHistoryItem]` - Get all queries ordered by newest first
  - `get_query_history_by_id(query_id: int) -> Optional[QueryHistoryDetailResponse]` - Get specific query
- Use JSON serialization for results and columns storage
- Call `init_query_history_table()` in `server.py` on startup

### Step 5: Backend API Endpoints
- Modify `/api/query` endpoint in `server.py`:
  - After successful query execution, call `save_query_history()` with query data
  - Generate display name using LLM (handle errors gracefully)
  - Save to database
- Add `GET /api/query-history` endpoint:
  - Return `QueryHistoryResponse` with all queries ordered by newest first
- Add `GET /api/query-history/{query_id}` endpoint:
  - Return `QueryHistoryDetailResponse` for specific query
  - Return 404 if query not found

### Step 6: Frontend API Client
- Add `getQueryHistory(): Promise<QueryHistoryResponse>` method to `api` object in `client.ts`
- Add `getQueryHistoryById(id: number): Promise<QueryHistoryDetailResponse>` method
- Follow existing `apiRequest` pattern

### Step 7: Side Panel HTML Structure
- Add side panel HTML in `index.html`:
  - `<div id="query-history-panel" class="query-history-panel">` (initially hidden)
  - Panel header with "Query History" title and close button
  - Scrollable list container `<div id="query-history-list" class="query-history-list">`
  - Empty state message for when no queries exist
- Add "Show Panel" button in query-controls div next to "Upload Data" button:
  - `<button id="show-history-button" class="secondary-button">Show Panel</button>`

### Step 8: Side Panel CSS Styling
- Add `.query-history-panel` styles in `style.css`:
  - Fixed positioning on right side (right: 0, top: 0, height: 100vh)
  - Width: 350px (or responsive)
  - Background: var(--surface)
  - Box shadow for depth
  - Transform: translateX(100%) when hidden (off-screen)
  - Transition for slide-in animation
  - z-index: 999 (below modal but above content)
- Add `.query-history-item` styles:
  - Padding, border, hover effects
  - Display name, timestamp, row count
  - Cursor pointer
- Add overlay background when panel is open (optional, for better UX)
- Use existing CSS variables for consistency

### Step 9: Panel Toggle Functionality
- Add `initializeQueryHistoryPanel()` function in `main.ts`:
  - Get "Show Panel" button and panel element
  - Toggle panel visibility on button click
  - Close button functionality
  - Close on overlay click (if overlay added)
- Add state variable `let isHistoryPanelOpen = false`
- Update button text to "Hide Panel" when open

### Step 10: History Loading and Display
- Add `loadQueryHistory()` async function:
  - Call `api.getQueryHistory()`
  - Clear existing list
  - Create DOM elements for each query item
  - Display empty state if no queries
- Add `displayQueryHistoryItem(item: QueryHistoryItem)` function:
  - Create clickable div with query info
  - Show display_name, timestamp (formatted), row_count
  - Add click handler to refocus query
- Call `loadQueryHistory()` on panel open and after successful queries

### Step 11: Query Refocusing
- Add `refocusQuery(queryId: number)` async function:
  - Call `api.getQueryHistoryById(queryId)`
  - Set `query-input` value to `query_text`
  - Call `displayResults()` with the stored results
  - Scroll to results section
  - Close panel (optional, or keep open)
- Attach click handlers to history items

### Step 12: Integration and Updates
- Modify `displayResults()` in `main.ts`:
  - After successful query display, call `loadQueryHistory()` to refresh panel if open
- Ensure history panel initializes on page load
- Test that queries are saved even if panel is closed

### Step 13: Error Handling and Edge Cases
- Handle LLM failures for display name generation (use fallback)
- Handle database errors gracefully
- Show error messages in panel if history fails to load
- Handle empty history state (show friendly message)
- Handle query not found (404) when refocusing

### Step 14: Testing
- Create unit tests for `query_history.py` functions
- Test database operations (save, retrieve, ordering)
- Test LLM display name generation with various query types
- Test API endpoints with Postman or similar
- Test frontend: panel toggle, history display, query refocusing
- Test persistence: refresh page, verify history persists

### Step 15: Validation
- Run validation commands to ensure feature works correctly with zero regressions

## Testing Strategy

### Unit Tests
- Test `save_query_history()` saves correctly with all fields
- Test `get_all_query_history()` returns queries ordered by newest first
- Test `get_query_history_by_id()` returns correct query or None
- Test `generate_query_display_name()` with various query types
- Test JSON serialization/deserialization of results and columns
- Test table initialization (idempotent)

### Integration Tests
- Test `/api/query` saves to history after successful execution
- Test `/api/query-history` returns correct format and ordering
- Test `/api/query-history/{id}` returns full query details
- Test error handling when LLM fails for display name
- Test database persistence across server restarts

### Edge Cases
- Empty history (no queries yet)
- Very long query text (truncation in display)
- Query with no results (row_count = 0)
- Failed queries (should not be saved to history)
- LLM provider unavailable (fallback to query text)
- Database connection errors
- Very large result sets (JSON serialization limits)
- Concurrent queries (thread safety)

## Acceptance Criteria

1. ✅ Query history table is created in database on server startup
2. ✅ Every successful query is automatically saved to history with all metadata
3. ✅ Display names are generated using LLM for each query
4. ✅ "Show Panel" button appears next to "Upload Data" button
5. ✅ Clicking "Show Panel" opens side panel from right side with slide animation
6. ✅ Panel displays all queries ordered by newest first
7. ✅ Each query item shows: display name, timestamp, row count
8. ✅ Clicking a query item refocuses main panel with that query's results
9. ✅ Query text is restored to input field when refocusing
10. ✅ History persists across page refreshes
11. ✅ Panel can be closed via close button or "Hide Panel" button
12. ✅ Empty state is shown when no queries exist
13. ✅ Panel updates automatically after new queries
14. ✅ All TypeScript types match Pydantic models
15. ✅ No regressions in existing functionality

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run python -c "from core.query_history import init_query_history_table; init_query_history_table(); print('Table created successfully')"` - Verify table creation
- `cd app/server && sqlite3 db/database.db "SELECT name FROM sqlite_master WHERE type='table' AND name='query_history';"` - Verify table exists
- `cd app/server && uv run python server.py` - Start server and verify no startup errors
- `cd app/client && npm run build` - Verify TypeScript compiles without errors
- `cd app/client && npm run dev` - Start frontend and manually test:
  - Click "Show Panel" button - panel should slide in from right
  - Execute a query - verify it appears in history
  - Click a history item - verify query refocuses
  - Refresh page - verify history persists
  - Test with multiple queries - verify ordering (newest first)
- `curl http://localhost:8000/api/query-history` - Verify API endpoint returns history
- `curl http://localhost:8000/api/query-history/1` - Verify specific query endpoint works
- Execute a query via API and verify it appears in history endpoint
- Test with empty history - verify empty state displays correctly
- Test LLM display name generation with various query types
- Verify no console errors in browser developer tools
- Verify CSS animations work smoothly
- Test on different screen sizes (responsive behavior)

## Notes

- **LLM Provider Selection**: The display name generation should use the same LLM provider routing logic as SQL generation for consistency. If LLM fails, fallback to truncated query text (first 50 chars).
- **Performance Considerations**: For large histories, consider pagination in the future. For now, load all queries (reasonable limit for MVP).
- **Storage Optimization**: Results are stored as JSON strings. For very large result sets, consider storing only metadata and fetching results on-demand, but for MVP, store everything.
- **Future Enhancements**: 
  - Search/filter queries
  - Delete queries from history
  - Export query history
  - Query templates/favorites
  - Share queries
- **Database Migration**: The table will be created automatically on first run. No migration script needed for MVP.
- **Type Safety**: Ensure TypeScript types in `types.d.ts` exactly match Pydantic models in `data_models.py` - this is critical for type safety.
- **Error Handling**: All LLM calls should have try-catch blocks with fallbacks. Database operations should handle connection errors gracefully.
- **UI/UX**: Panel should feel responsive and smooth. Consider adding loading states when fetching history. The slide-in animation should be subtle (300ms transition).




