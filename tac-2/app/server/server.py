from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sqlite3
import traceback
from typing import Optional
from dotenv import load_dotenv

# Load .env file from server directory
load_dotenv()

from core.data_models import (
    FileUploadResponse,
    QueryRequest,
    QueryResponse,
    DatabaseSchemaResponse,
    InsightsRequest,
    InsightsResponse,
    HealthCheckResponse,
    TableSchema,
    ColumnInfo
)

# Import core modules (to be implemented)
from core.file_processor import convert_csv_to_sqlite, convert_json_to_sqlite
from core.llm_processor import generate_sql
from core.sql_processor import execute_sql_safely, get_database_schema
from core.insights import generate_insights

app = FastAPI(
    title="Natural Language SQL Interface",
    description="Convert natural language to SQL queries",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global app state
app_start_time = datetime.now()

# Ensure database directory exists
os.makedirs("db", exist_ok=True)

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """Upload and convert .json or .csv file to SQLite table"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(400, "Only .csv and .json files are supported")
        
        # Generate table name from filename
        table_name = file.filename.rsplit('.', 1)[0].lower().replace(' ', '_')
        
        # Read file content
        content = await file.read()
        
        # Convert to SQLite based on file type
        if file.filename.endswith('.csv'):
            result = convert_csv_to_sqlite(content, table_name)
        else:
            result = convert_json_to_sqlite(content, table_name)
        
        response = FileUploadResponse(
            table_name=result['table_name'],
            table_schema=result['schema'],
            row_count=result['row_count'],
            sample_data=result['sample_data']
        )
        print("SUCCESS: /api/upload")
        print(f"Response: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print("EXCEPTION: /api/upload")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        response = FileUploadResponse(
            table_name="",
            table_schema={},
            row_count=0,
            sample_data=[],
            error=str(e)
        )
        print(f"Error response: {response.model_dump_json(indent=2)}")
        return response

@app.post("/api/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest) -> QueryResponse:
    """Process natural language query and return SQL results"""
    try:
        # Get database schema
        schema_info = get_database_schema()
        
        # Generate SQL using routing logic
        sql = generate_sql(request, schema_info)
        
        # Execute SQL query
        start_time = datetime.now()
        result = execute_sql_safely(sql)
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if result['error']:
            raise Exception(result['error'])
        
        response = QueryResponse(
            sql=sql,
            results=result['results'],
            columns=result['columns'],
            row_count=len(result['results']),
            execution_time_ms=execution_time
        )
        print("SUCCESS: /api/query")
        print(f"Response: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print("EXCEPTION: /api/query")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        response = QueryResponse(
            sql="",
            results=[],
            columns=[],
            row_count=0,
            execution_time_ms=0,
            error=str(e)
        )
        print(f"Error response: {response.model_dump_json(indent=2)}")
        return response

@app.get("/api/schema", response_model=DatabaseSchemaResponse)
async def get_database_schema_endpoint() -> DatabaseSchemaResponse:
    """Get current database schema and table information"""
    try:
        schema = get_database_schema()
        tables = []
        
        for table_name, table_info in schema['tables'].items():
            columns = []
            for col_name, col_type in table_info['columns'].items():
                columns.append(ColumnInfo(
                    name=col_name,
                    type=col_type,
                    nullable=True,
                    primary_key=False
                ))
            
            tables.append(TableSchema(
                name=table_name,
                columns=columns,
                row_count=table_info.get('row_count', 0),
                created_at=datetime.now()  # Simplified for v1
            ))
        
        response = DatabaseSchemaResponse(
            tables=tables,
            total_tables=len(tables)
        )
        print("SUCCESS: /api/schema")
        print(f"Response: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print("EXCEPTION: /api/schema")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        response = DatabaseSchemaResponse(
            tables=[],
            total_tables=0,
            error=str(e)
        )
        print(f"Error response: {response.model_dump_json(indent=2)}")
        return response

@app.post("/api/insights", response_model=InsightsResponse)
async def generate_insights_endpoint(request: InsightsRequest) -> InsightsResponse:
    """Generate statistical insights for table columns"""
    try:
        insights = generate_insights(request.table_name, request.column_names)
        response = InsightsResponse(
            table_name=request.table_name,
            insights=insights,
            generated_at=datetime.now()
        )
        print("SUCCESS: /api/insights")
        print(f"Response: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print("EXCEPTION: /api/insights")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        response = InsightsResponse(
            table_name=request.table_name,
            insights=[],
            generated_at=datetime.now(),
            error=str(e)
        )
        print(f"Error response: {response.model_dump_json(indent=2)}")
        return response

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint with database status"""
    try:
        # Check database connection
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        uptime = (datetime.now() - app_start_time).total_seconds()
        
        response = HealthCheckResponse(
            status="ok",
            database_connected=True,
            tables_count=len(tables),
            uptime_seconds=uptime
        )
        print("SUCCESS: /api/health")
        print(f"Response: {response.model_dump_json(indent=2)}")
        return response
    except Exception as e:
        print("EXCEPTION: /api/health")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        response = HealthCheckResponse(
            status="error",
            database_connected=False,
            tables_count=0,
            uptime_seconds=0
        )
        print(f"Error response: {response.model_dump_json(indent=2)}")
        return response

@app.delete("/api/table/{table_name}")
async def delete_table(table_name: str):
    """Delete a table from the database"""
    try:
        # Validate table name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise HTTPException(400, "Invalid table name")
        
        conn = sqlite3.connect("db/database.db")
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(404, f"Table '{table_name}' not found")
        
        # Drop the table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()
        
        response = {"message": f"Table '{table_name}' deleted successfully"}
        print("SUCCESS: /api/table/{table_name} DELETE")
        print(f"Response: {response}")
        return response
    except HTTPException as e:
        print("HTTP EXCEPTION: /api/table/{table_name} DELETE")
        print(f"HTTPException status_code: {e.status_code}")
        print(f"HTTPException detail: {e.detail}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        raise
    except Exception as e:
        print("EXCEPTION: /api/table/{table_name} DELETE")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(500, f"Error deleting table: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)