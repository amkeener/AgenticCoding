import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.data_models import QueryHistoryItem, QueryHistoryDetailResponse
from core.llm_processor import generate_query_display_name

def init_query_history_table():
    """
    Initialize the query_history table if it doesn't exist
    """
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text TEXT NOT NULL,
            sql TEXT NOT NULL,
            display_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            results TEXT,
            columns TEXT,
            row_count INTEGER DEFAULT 0,
            execution_time_ms REAL DEFAULT 0
        )
    """)
    
    # Create index on created_at for faster ordering
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_query_history_created_at 
        ON query_history(created_at DESC)
    """)
    
    conn.commit()
    conn.close()

def save_query_history(
    query_text: str,
    sql: str,
    results: List[Dict[str, Any]],
    columns: List[str],
    row_count: int,
    execution_time_ms: float,
    llm_provider: str = None
) -> int:
    """
    Save a completed query to history.
    Generates a display name using LLM.
    Returns the ID of the saved query.
    """
    # Generate display name using LLM
    try:
        display_name = generate_query_display_name(query_text, sql, llm_provider)
    except Exception as e:
        # Fallback to truncated query text if LLM fails
        display_name = query_text[:50] if len(query_text) > 50 else query_text
    
    # Convert results and columns to JSON strings
    results_json = json.dumps(results)
    columns_json = json.dumps(columns)
    
    conn = sqlite3.connect("db/database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO query_history 
        (query_text, sql, display_name, results, columns, row_count, execution_time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (query_text, sql, display_name, results_json, columns_json, row_count, execution_time_ms))
    
    query_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return query_id

def get_all_query_history() -> List[QueryHistoryItem]:
    """
    Get all query history items, ordered by newest first
    """
    conn = sqlite3.connect("db/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, query_text, sql, display_name, created_at, row_count, execution_time_ms
        FROM query_history
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    queries = []
    for row in rows:
        queries.append(QueryHistoryItem(
            id=row['id'],
            query_text=row['query_text'],
            sql=row['sql'],
            display_name=row['display_name'],
            created_at=datetime.fromisoformat(row['created_at']),
            row_count=row['row_count'],
            execution_time_ms=row['execution_time_ms']
        ))
    
    return queries

def get_query_history_by_id(query_id: int) -> Optional[QueryHistoryDetailResponse]:
    """
    Get a specific query history item by ID with full details
    """
    conn = sqlite3.connect("db/database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, query_text, sql, display_name, created_at, results, columns, 
               row_count, execution_time_ms
        FROM query_history
        WHERE id = ?
    """, (query_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    # Parse JSON strings
    results = json.loads(row['results']) if row['results'] else []
    columns = json.loads(row['columns']) if row['columns'] else []
    
    return QueryHistoryDetailResponse(
        id=row['id'],
        query_text=row['query_text'],
        sql=row['sql'],
        display_name=row['display_name'],
        created_at=datetime.fromisoformat(row['created_at']),
        results=results,
        columns=columns,
        row_count=row['row_count'],
        execution_time_ms=row['execution_time_ms']
    )

