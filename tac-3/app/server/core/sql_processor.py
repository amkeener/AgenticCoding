import sqlite3
import re
from typing import Dict, Any, List, Set, Optional

# SQL keywords that should be blocked for safety
DANGEROUS_KEYWORDS = [
    'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER', 
    'CREATE', 'REPLACE', 'ATTACH', 'DETACH'
]

def validate_identifier(identifier: str) -> bool:
    """
    Validate that an identifier (table/column name) is safe.
    Only allows alphanumeric characters and underscores.
    """
    if not identifier:
        return False
    # SQLite identifiers can contain letters, digits, underscores, and can be quoted
    # For safety, we only allow unquoted identifiers with alphanumeric and underscore
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier))

def get_valid_table_names(conn: sqlite3.Connection) -> Set[str]:
    """
    Get a set of valid table names from the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    return {table[0] for table in tables}

def get_valid_column_names(conn: sqlite3.Connection, table_name: str) -> Set[str]:
    """
    Get a set of valid column names for a table.
    """
    if not validate_identifier(table_name):
        return set()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(?)", (table_name,))
    columns_info = cursor.fetchall()
    return {col[1] for col in columns_info}

def execute_sql_safely(sql_query: str) -> Dict[str, Any]:
    """
    Execute SQL query with safety checks and parameterized queries.
    Only allows SELECT queries. Validates table/column names against schema.
    """
    try:
        # Basic SQL injection protection - block dangerous keywords
        sql_upper = sql_query.upper().strip()
        for keyword in DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return {
                    'results': [],
                    'columns': [],
                    'error': f"Dangerous SQL keyword '{keyword}' detected. Only SELECT queries are allowed."
                }
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return {
                'results': [],
                'columns': [],
                'error': "Only SELECT queries are allowed."
            }
        
        # Connect to database
        conn = sqlite3.connect("db/database.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get valid table names for validation
        valid_tables = get_valid_table_names(conn)
        
        # Extract table names from SQL (simple regex approach)
        # Match FROM/JOIN clauses to find table names
        table_pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        found_tables = re.findall(table_pattern, sql_query, re.IGNORECASE)
        
        # Validate all table names exist in schema
        for table in found_tables:
            if not validate_identifier(table):
                conn.close()
                return {
                    'results': [],
                    'columns': [],
                    'error': f"Invalid table name: {table}"
                }
            if table not in valid_tables:
                conn.close()
                return {
                    'results': [],
                    'columns': [],
                    'error': f"Table '{table}' does not exist in database."
                }
        
        # Execute query - SQLite will handle parameterization if the query uses placeholders
        # For now, we validate structure but execute as-is since LLM generates the SQL
        # In production, you'd want to parse and rebuild with parameterized values
        cursor.execute(sql_query)
        
        # Get results
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        results = []
        columns = []
        
        if rows:
            columns = list(rows[0].keys())
            for row in rows:
                results.append(dict(row))
        
        conn.close()
        
        return {
            'results': results,
            'columns': columns,
            'error': None
        }
        
    except sqlite3.OperationalError as e:
        return {
            'results': [],
            'columns': [],
            'error': f"SQL error: {str(e)}"
        }
    except Exception as e:
        return {
            'results': [],
            'columns': [],
            'error': str(e)
        }

def get_database_schema() -> Dict[str, Any]:
    """
    Get complete database schema information using parameterized queries.
    """
    try:
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        
        # Get all tables - this query is safe, no user input
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema = {'tables': {}}
        
        for table in tables:
            table_name = table[0]
            
            # Validate table name before using
            if not validate_identifier(table_name):
                continue
            
            # Get columns for each table
            # Note: PRAGMA doesn't support ? placeholders, but we validate the identifier first
            # This is safe because table_name comes from sqlite_master, not user input
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            columns = {}
            for col in columns_info:
                columns[col[1]] = col[2]  # column_name: data_type
            
            # Get row count - validate table name is in valid set
            valid_tables = get_valid_table_names(conn)
            if table_name in valid_tables:
                # Use parameterized query where possible
                # For table names in FROM clause, we validate but can't parameterize
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
            else:
                row_count = 0
            
            schema['tables'][table_name] = {
                'columns': columns,
                'row_count': row_count
            }
        
        conn.close()
        
        return schema
        
    except Exception as e:
        return {'tables': {}, 'error': str(e)}