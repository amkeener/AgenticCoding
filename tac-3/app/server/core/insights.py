import sqlite3
from typing import List, Optional, Dict, Any, Set
from core.data_models import ColumnInsight
from core.sql_processor import validate_identifier, get_valid_table_names, get_valid_column_names

def generate_insights(table_name: str, column_names: Optional[List[str]] = None) -> List[ColumnInsight]:
    """
    Generate statistical insights for table columns.
    Validates table and column names against schema before use.
    """
    try:
        # Validate table name
        if not validate_identifier(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        
        # Validate table exists
        valid_tables = get_valid_table_names(conn)
        if table_name not in valid_tables:
            conn.close()
            raise ValueError(f"Table '{table_name}' does not exist in database.")
        
        # Get valid column names for this table
        valid_columns = get_valid_column_names(conn, table_name)
        
        # Get table schema - safe because table_name is validated
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        # If no specific columns requested, analyze all
        if not column_names:
            column_names = [col[1] for col in columns_info]
        else:
            # Validate all requested column names exist
            for col_name in column_names:
                if not validate_identifier(col_name):
                    conn.close()
                    raise ValueError(f"Invalid column name: {col_name}")
                if col_name not in valid_columns:
                    conn.close()
                    raise ValueError(f"Column '{col_name}' does not exist in table '{table_name}'.")
        
        insights = []
        
        for col_info in columns_info:
            col_name = col_info[1]
            col_type = col_info[2]
            
            # Validate column name before use
            if not validate_identifier(col_name):
                continue
            
            if col_name not in column_names:
                continue
            
            # Basic statistics - identifiers are validated, safe to use
            cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
            unique_values = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
            null_count = cursor.fetchone()[0]
            
            insight = ColumnInsight(
                column_name=col_name,
                data_type=col_type,
                unique_values=unique_values,
                null_count=null_count
            )
            
            # Type-specific insights
            if col_type in ['INTEGER', 'REAL', 'NUMERIC']:
                # Numeric insights
                cursor.execute(f"""
                    SELECT 
                        MIN({col_name}) as min_val,
                        MAX({col_name}) as max_val,
                        AVG({col_name}) as avg_val
                    FROM {table_name}
                    WHERE {col_name} IS NOT NULL
                """)
                result = cursor.fetchone()
                if result:
                    insight.min_value = result[0]
                    insight.max_value = result[1]
                    insight.avg_value = result[2]
            
            # Most common values (for all types)
            cursor.execute(f"""
                SELECT {col_name}, COUNT(*) as count
                FROM {table_name}
                WHERE {col_name} IS NOT NULL
                GROUP BY {col_name}
                ORDER BY count DESC
                LIMIT 5
            """)
            most_common = cursor.fetchall()
            if most_common:
                insight.most_common = [
                    {"value": val, "count": count} 
                    for val, count in most_common
                ]
            
            insights.append(insight)
        
        conn.close()
        return insights
        
    except Exception as e:
        raise Exception(f"Error generating insights: {str(e)}")