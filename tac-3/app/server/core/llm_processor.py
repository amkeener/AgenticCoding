import os
import json
import subprocess
import requests
from typing import Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from core.data_models import QueryRequest

def generate_sql_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions

SQL Query:"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Convert natural language to SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with OpenAI: {str(e)}")

def generate_sql_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions

SQL Query:"""
        
        # Call Anthropic API
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        sql = response.content[0].text.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with Anthropic: {str(e)}")

def generate_sql_with_ollama(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using Ollama API
    """
    try:
        # Get Ollama configuration from environment
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b")
        # Context size: default 4096 tokens, can be increased for larger schemas
        # Note: Increasing context requires more memory (VRAM)
        ollama_num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "4096"))
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt with system message for better results
        system_prompt = "You are a SQL expert. Convert natural language to SQL queries. Return ONLY the SQL query, no explanations."
        user_prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions

SQL Query:"""
        
        # Try /api/generate endpoint first (more compatible, avoids 401 errors)
        # Some Ollama versions/configurations return 401 for /api/chat
        api_url = f"{ollama_base_url}/api/generate"
        payload = {
            "model": ollama_model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500,
                "num_ctx": ollama_num_ctx  # Context window size (default: 4096 tokens)
            }
        }
        
        sql = None
        result = None
        
        try:
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            sql = result.get("response", "").strip()
        except requests.exceptions.HTTPError as e:
            # If generate endpoint fails with 401 or other error, try /api/chat as fallback
            if e.response and e.response.status_code == 401:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Generate endpoint returned 401, trying chat endpoint as fallback")
                
                # Fallback to /api/chat
                api_url = f"{ollama_base_url}/api/chat"
                payload = {
                    "model": ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 500,
                        "num_ctx": ollama_num_ctx
                    }
                }
                
                try:
                    response = requests.post(api_url, json=payload, timeout=120)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract response from chat format
                    if "message" in result and "content" in result["message"]:
                        sql = result["message"]["content"].strip()
                    elif "response" in result:
                        sql = result["response"].strip()
                except Exception as chat_error:
                    # Re-raise the original error if chat also fails
                    raise e
            else:
                # Re-raise non-401 errors
                raise
        
        if not sql:
            # Log the full response for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Empty response from Ollama. Model: {ollama_model}, Full response: {result}")
            
            # Provide helpful error message
            error_msg = f"Empty response from Ollama. Model: '{ollama_model}'"
            if result:
                error_msg += f". Response keys: {list(result.keys())}"
            error_msg += f". Please verify: 1) Model '{ollama_model}' exists (run 'ollama list'), 2) Ollama is running, 3) Model name is correct."
            raise Exception(error_msg)
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except requests.exceptions.Timeout:
        raise Exception(f"Ollama API request timed out. Model: {ollama_model} may be slow or unavailable.")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Cannot connect to Ollama at {ollama_base_url}. Is Ollama running? Error: {str(e)}")
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_response = e.response.json() if e.response else {}
            error_detail = f" Response: {error_response}"
        except:
            error_detail = f" Status: {e.response.status_code if e.response else 'unknown'}"
        raise Exception(f"Ollama API HTTP error: {str(e)}{error_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to Ollama API: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating SQL with Ollama: {str(e)}")

def generate_sql_with_cursor_agent(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using cursor-agent CLI
    """
    try:
        # Check if cursor-agent is available
        result = subprocess.run(
            ["which", "cursor-agent"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise Exception("cursor-agent command not found. Please install it: curl https://cursor.com/install -fsS | bash")
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions

SQL Query:"""
        
        # Call cursor-agent CLI
        command = [
            "cursor-agent",
            "--print",
            "--force",
            prompt
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"cursor-agent failed with return code {result.returncode}. Error: {result.stderr}")
        
        sql = result.stdout.strip()
        
        if not sql:
            raise Exception("Empty response from cursor-agent")
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except subprocess.TimeoutExpired:
        raise Exception("cursor-agent command timed out after 60 seconds")
    except FileNotFoundError:
        raise Exception("cursor-agent command not found. Please install it: curl https://cursor.com/install -fsS | bash")
    except Exception as e:
        raise Exception(f"Error generating SQL with cursor-agent: {str(e)}")

def generate_sql_with_claude(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using claude CLI
    """
    try:
        # Check if claude is available
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise Exception("claude command not found. Please install the Claude CLI.")
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions

SQL Query:"""
        
        # Call claude CLI
        command = [
            "claude",
            "-p",
            prompt
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"claude failed with return code {result.returncode}. Error: {result.stderr}")
        
        sql = result.stdout.strip()
        
        if not sql:
            raise Exception("Empty response from claude")
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except subprocess.TimeoutExpired:
        raise Exception("claude command timed out after 60 seconds")
    except FileNotFoundError:
        raise Exception("claude command not found. Please install the Claude CLI.")
    except Exception as e:
        raise Exception(f"Error generating SQL with claude: {str(e)}")

def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Format database schema for LLM prompt
    """
    lines = []
    
    for table_name, table_info in schema_info.get('tables', {}).items():
        lines.append(f"Table: {table_name}")
        lines.append("Columns:")
        
        for col_name, col_type in table_info['columns'].items():
            lines.append(f"  - {col_name} ({col_type})")
        
        lines.append(f"Row count: {table_info['row_count']}")
        lines.append("")
    
    return "\n".join(lines)

def generate_sql(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider based on API key availability and request preference.
    Priority: 1) request.llm_provider if specified, 2) OpenAI API key exists, 3) Anthropic API key exists, 4) cursor-agent, 5) claude, 6) Ollama
    """
    # If specific provider is requested, use it
    if request.llm_provider == "ollama":
        return generate_sql_with_ollama(request.query, schema_info)
    elif request.llm_provider == "openai":
        return generate_sql_with_openai(request.query, schema_info)
    elif request.llm_provider == "anthropic":
        return generate_sql_with_anthropic(request.query, schema_info)
    elif request.llm_provider == "cursor-agent":
        return generate_sql_with_cursor_agent(request.query, schema_info)
    elif request.llm_provider == "claude":
        return generate_sql_with_claude(request.query, schema_info)
    
    # Fall back to API key availability (OpenAI priority)
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if openai_key:
        return generate_sql_with_openai(request.query, schema_info)
    elif anthropic_key:
        return generate_sql_with_anthropic(request.query, schema_info)
    else:
        # Try CLI agents, then Ollama
        try:
            # Check if cursor-agent is available
            result = subprocess.run(["which", "cursor-agent"], capture_output=True, timeout=2)
            if result.returncode == 0:
                return generate_sql_with_cursor_agent(request.query, schema_info)
        except:
            pass
        
        try:
            # Check if claude is available
            result = subprocess.run(["which", "claude"], capture_output=True, timeout=2)
            if result.returncode == 0:
                return generate_sql_with_claude(request.query, schema_info)
        except:
            pass
        
        # Default to Ollama if no API keys or CLI agents available
        return generate_sql_with_ollama(request.query, schema_info)

def generate_display_name_with_openai(query_text: str, sql: str) -> str:
    """
    Generate a concise display name for a query using OpenAI API
    """
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Generate a concise, descriptive name (max 50 characters) for this query: "{query_text}" with SQL: "{sql}". Return only the name, no quotes or explanations."""
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates concise, descriptive names for database queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        name = response.choices[0].message.content.strip()
        
        # Remove quotes if present
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        
        # Truncate to 50 chars if needed
        return name[:50].strip()
        
    except Exception as e:
        raise Exception(f"Error generating display name with OpenAI: {str(e)}")

def generate_display_name_with_anthropic(query_text: str, sql: str) -> str:
    """
    Generate a concise display name for a query using Anthropic API
    """
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        prompt = f"""Generate a concise, descriptive name (max 50 characters) for this query: "{query_text}" with SQL: "{sql}". Return only the name, no quotes or explanations."""
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        name = response.content[0].text.strip()
        
        # Remove quotes if present
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        
        # Truncate to 50 chars if needed
        return name[:50].strip()
        
    except Exception as e:
        raise Exception(f"Error generating display name with Anthropic: {str(e)}")

def generate_display_name_with_ollama(query_text: str, sql: str) -> str:
    """
    Generate a concise display name for a query using Ollama API
    """
    try:
        # Get Ollama configuration from environment
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b")
        # Context size for display name generation (can be smaller since prompts are shorter)
        ollama_num_ctx = int(os.environ.get("OLLAMA_NUM_CTX", "4096"))
        
        system_prompt = "You are a helpful assistant that generates concise, descriptive names for database queries."
        user_prompt = f"""Generate a concise, descriptive name (max 50 characters) for this query: "{query_text}" with SQL: "{sql}". Return only the name, no quotes or explanations."""
        
        # Try /api/generate endpoint first (more compatible, avoids 401 errors)
        api_url = f"{ollama_base_url}/api/generate"
        payload = {
            "model": ollama_model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 50,
                "num_ctx": ollama_num_ctx  # Context window size
            }
        }
        
        name = None
        result = None
        
        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            name = result.get("response", "").strip()
        except requests.exceptions.HTTPError as e:
            # If generate endpoint fails with 401 or other error, try /api/chat as fallback
            if e.response and e.response.status_code == 401:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Generate endpoint returned 401 for display name, trying chat endpoint as fallback")
                
                # Fallback to /api/chat
                api_url = f"{ollama_base_url}/api/chat"
                payload = {
                    "model": ollama_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 50,
                        "num_ctx": ollama_num_ctx
                    }
                }
                
                try:
                    response = requests.post(api_url, json=payload, timeout=60)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract response from chat format
                    if "message" in result and "content" in result["message"]:
                        name = result["message"]["content"].strip()
                    elif "response" in result:
                        name = result["response"].strip()
                except Exception as chat_error:
                    # Re-raise the original error if chat also fails
                    raise e
            else:
                # Re-raise non-401 errors
                raise
        
        if not name:
            error_msg = f"Empty response from Ollama for display name. Model: '{ollama_model}'"
            if result:
                error_msg += f". Response keys: {list(result.keys())}"
            raise Exception(error_msg)
        
        # Remove quotes if present
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        elif name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        
        # Truncate to 50 chars if needed
        return name[:50].strip()
        
    except requests.exceptions.Timeout:
        raise Exception(f"Ollama API request timed out. Model: {ollama_model} may be slow or unavailable.")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Cannot connect to Ollama at {ollama_base_url}. Is Ollama running? Error: {str(e)}")
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_response = e.response.json() if e.response else {}
            error_detail = f" Response: {error_response}"
        except:
            error_detail = f" Status: {e.response.status_code if e.response else 'unknown'}"
        raise Exception(f"Ollama API HTTP error: {str(e)}{error_detail}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to Ollama API: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating display name with Ollama: {str(e)}")

def generate_query_display_name(query_text: str, sql: str, llm_provider: str = None) -> str:
    """
    Generate a concise display name for a query using available LLM provider.
    Uses same routing logic as generate_sql.
    """
    # If specific provider is requested, use it
    if llm_provider == "ollama":
        try:
            return generate_display_name_with_ollama(query_text, sql)
        except Exception:
            # Fall through to fallback
            pass
    elif llm_provider == "openai":
        try:
            return generate_display_name_with_openai(query_text, sql)
        except Exception:
            # Fall through to fallback
            pass
    elif llm_provider == "anthropic":
        try:
            return generate_display_name_with_anthropic(query_text, sql)
        except Exception:
            # Fall through to fallback
            pass
    elif llm_provider == "cursor-agent" or llm_provider == "claude":
        # CLI agents don't have display name generation, fall through to API fallback
        pass
    
    # Fall back to API key availability (OpenAI priority)
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if openai_key:
        try:
            return generate_display_name_with_openai(query_text, sql)
        except Exception:
            # Fall through to Anthropic or fallback
            pass
    
    if anthropic_key:
        try:
            return generate_display_name_with_anthropic(query_text, sql)
        except Exception:
            # Fall through to fallback
            pass
    
    # Try Ollama as fallback
    try:
        return generate_display_name_with_ollama(query_text, sql)
    except Exception:
        # Final fallback: truncate query text
        pass
    
    # Final fallback: truncate query text
    return query_text[:50] if len(query_text) > 50 else query_text