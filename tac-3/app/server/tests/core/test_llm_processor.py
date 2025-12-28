import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from core.llm_processor import (
    generate_sql_with_openai, 
    generate_sql_with_anthropic,
    generate_sql_with_cursor_agent,
    generate_sql_with_claude,
    format_schema_for_prompt,
    generate_sql
)
from core.data_models import QueryRequest


class TestLLMProcessor:
    
    @patch('core.llm_processor.OpenAI')
    def test_generate_sql_with_openai_success(self, mock_openai_class):
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "SELECT * FROM users WHERE age > 25"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Mock environment variable
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            query_text = "Show me users older than 25"
            schema_info = {
                'tables': {
                    'users': {
                        'columns': {'id': 'INTEGER', 'name': 'TEXT', 'age': 'INTEGER'},
                        'row_count': 100
                    }
                }
            }
            
            result = generate_sql_with_openai(query_text, schema_info)
            
            assert result == "SELECT * FROM users WHERE age > 25"
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify the API call parameters
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'gpt-4.1-mini'
            assert call_args[1]['temperature'] == 0.1
            assert call_args[1]['max_tokens'] == 500
    
    @patch('core.llm_processor.OpenAI')
    def test_generate_sql_with_openai_clean_markdown(self, mock_openai_class):
        # Test SQL cleanup from markdown
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "```sql\nSELECT * FROM users\n```"
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            query_text = "Show all users"
            schema_info = {'tables': {}}
            
            result = generate_sql_with_openai(query_text, schema_info)
            
            assert result == "SELECT * FROM users"
    
    def test_generate_sql_with_openai_no_api_key(self):
        # Test error when API key is not set
        with patch.dict(os.environ, {}, clear=True):
            query_text = "Show all users"
            schema_info = {'tables': {}}
            
            with pytest.raises(Exception) as exc_info:
                generate_sql_with_openai(query_text, schema_info)
            
            assert "OPENAI_API_KEY environment variable not set" in str(exc_info.value)
    
    @patch('core.llm_processor.OpenAI')
    def test_generate_sql_with_openai_api_error(self, mock_openai_class):
        # Test API error handling
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            query_text = "Show all users"
            schema_info = {'tables': {}}
            
            with pytest.raises(Exception) as exc_info:
                generate_sql_with_openai(query_text, schema_info)
            
            assert "Error generating SQL with OpenAI" in str(exc_info.value)
    
    @patch('core.llm_processor.Anthropic')
    def test_generate_sql_with_anthropic_success(self, mock_anthropic_class):
        # Mock Anthropic client and response
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content[0].text = "SELECT * FROM products WHERE price < 100"
        mock_client.messages.create.return_value = mock_response
        
        # Mock environment variable
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            query_text = "Show me products under $100"
            schema_info = {
                'tables': {
                    'products': {
                        'columns': {'id': 'INTEGER', 'name': 'TEXT', 'price': 'REAL'},
                        'row_count': 50
                    }
                }
            }
            
            result = generate_sql_with_anthropic(query_text, schema_info)
            
            assert result == "SELECT * FROM products WHERE price < 100"
            mock_client.messages.create.assert_called_once()
            
            # Verify the API call parameters
            call_args = mock_client.messages.create.call_args
            assert call_args[1]['model'] == 'claude-3-haiku-20240307'
            assert call_args[1]['temperature'] == 0.1
            assert call_args[1]['max_tokens'] == 500
    
    @patch('core.llm_processor.Anthropic')
    def test_generate_sql_with_anthropic_clean_markdown(self, mock_anthropic_class):
        # Test SQL cleanup from markdown
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.content[0].text = "```\nSELECT * FROM orders\n```"
        mock_client.messages.create.return_value = mock_response
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            query_text = "Show all orders"
            schema_info = {'tables': {}}
            
            result = generate_sql_with_anthropic(query_text, schema_info)
            
            assert result == "SELECT * FROM orders"
    
    def test_generate_sql_with_anthropic_no_api_key(self):
        # Test error when API key is not set
        with patch.dict(os.environ, {}, clear=True):
            query_text = "Show all orders"
            schema_info = {'tables': {}}
            
            with pytest.raises(Exception) as exc_info:
                generate_sql_with_anthropic(query_text, schema_info)
            
            assert "ANTHROPIC_API_KEY environment variable not set" in str(exc_info.value)
    
    @patch('core.llm_processor.Anthropic')
    def test_generate_sql_with_anthropic_api_error(self, mock_anthropic_class):
        # Test API error handling
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            query_text = "Show all orders"
            schema_info = {'tables': {}}
            
            with pytest.raises(Exception) as exc_info:
                generate_sql_with_anthropic(query_text, schema_info)
            
            assert "Error generating SQL with Anthropic" in str(exc_info.value)
    
    def test_format_schema_for_prompt(self):
        # Test schema formatting for LLM prompt
        schema_info = {
            'tables': {
                'users': {
                    'columns': {'id': 'INTEGER', 'name': 'TEXT', 'age': 'INTEGER'},
                    'row_count': 100
                },
                'products': {
                    'columns': {'id': 'INTEGER', 'name': 'TEXT', 'price': 'REAL'},
                    'row_count': 50
                }
            }
        }
        
        result = format_schema_for_prompt(schema_info)
        
        assert "Table: users" in result
        assert "Table: products" in result
        assert "- id (INTEGER)" in result
        assert "- name (TEXT)" in result
        assert "- age (INTEGER)" in result
        assert "- price (REAL)" in result
        assert "Row count: 100" in result
        assert "Row count: 50" in result
    
    def test_format_schema_for_prompt_empty(self):
        # Test with empty schema
        schema_info = {'tables': {}}
        
        result = format_schema_for_prompt(schema_info)
        
        assert result == ""
    
    @patch('core.llm_processor.generate_sql_with_anthropic')
    def test_generate_sql_request_provider_priority(self, mock_anthropic_func):
        # Test that request provider takes priority over API keys
        mock_anthropic_func.return_value = "SELECT * FROM users"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'openai-key', 'ANTHROPIC_API_KEY': 'anthropic-key'}):
            request = QueryRequest(query="Show all users", llm_provider="anthropic")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM users"
            mock_anthropic_func.assert_called_once_with("Show all users", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_openai')
    def test_generate_sql_request_provider_openai(self, mock_openai_func):
        # Test that request provider is respected even when other keys exist
        mock_openai_func.return_value = "SELECT * FROM products"
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'anthropic-key'}, clear=True):
            request = QueryRequest(query="Show all products", llm_provider="openai")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM products"
            mock_openai_func.assert_called_once_with("Show all products", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_openai')
    def test_generate_sql_request_preference_openai(self, mock_openai_func):
        # Test request preference when no keys available
        mock_openai_func.return_value = "SELECT * FROM orders"
        
        with patch.dict(os.environ, {}, clear=True):
            request = QueryRequest(query="Show all orders", llm_provider="openai")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM orders"
            mock_openai_func.assert_called_once_with("Show all orders", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_anthropic')
    def test_generate_sql_request_preference_anthropic(self, mock_anthropic_func):
        # Test request preference when no keys available
        mock_anthropic_func.return_value = "SELECT * FROM customers"
        
        with patch.dict(os.environ, {}, clear=True):
            request = QueryRequest(query="Show all customers", llm_provider="anthropic")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM customers"
            mock_anthropic_func.assert_called_once_with("Show all customers", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_anthropic')
    def test_generate_sql_request_provider_anthropic(self, mock_anthropic_func):
        # Test that request provider is respected when both keys exist
        mock_anthropic_func.return_value = "SELECT * FROM inventory"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'openai-key', 'ANTHROPIC_API_KEY': 'anthropic-key'}):
            request = QueryRequest(query="Show inventory", llm_provider="anthropic")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM inventory"
            mock_anthropic_func.assert_called_once_with("Show inventory", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_openai')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_openai_key_fallback(self, mock_is_available, mock_openai_func):
        # Test OpenAI fallback when request provider not available and OpenAI key exists
        mock_is_available.return_value = False
        mock_openai_func.return_value = "SELECT * FROM sales"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'openai-key'}, clear=True):
            request = QueryRequest(query="Show sales data", llm_provider="openai")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM sales"
            mock_openai_func.assert_called_once_with("Show sales data", schema_info)
    
    @patch('core.llm_processor.subprocess.run')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_with_cursor_agent_success(self, mock_is_available, mock_subprocess):
        # Mock CLI availability
        mock_is_available.return_value = True
        
        # Mock subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SELECT * FROM users WHERE age > 25"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        query_text = "Show me users older than 25"
        schema_info = {
            'tables': {
                'users': {
                    'columns': {'id': 'INTEGER', 'name': 'TEXT', 'age': 'INTEGER'},
                    'row_count': 100
                }
            }
        }
        
        result = generate_sql_with_cursor_agent(query_text, schema_info)
        
        assert result == "SELECT * FROM users WHERE age > 25"
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[0][0][0] == "cursor-agent"
        assert "--print" in call_args[0][0]
        assert "--force" in call_args[0][0]
    
    @patch('core.llm_processor.shutil.which')
    def test_generate_sql_with_cursor_agent_not_available(self, mock_which):
        # Mock CLI not available
        mock_which.return_value = None
        
        query_text = "Show all users"
        schema_info = {'tables': {}}
        
        with pytest.raises(ValueError) as exc_info:
            generate_sql_with_cursor_agent(query_text, schema_info)
        
        assert "cursor-agent command not found" in str(exc_info.value)
    
    @patch('core.llm_processor.subprocess.run')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_with_cursor_agent_timeout(self, mock_is_available, mock_subprocess):
        # Mock CLI availability
        mock_is_available.return_value = True
        
        # Mock timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("cursor-agent", 60)
        
        query_text = "Show all users"
        schema_info = {'tables': {}}
        
        with pytest.raises(Exception) as exc_info:
            generate_sql_with_cursor_agent(query_text, schema_info)
        
        assert "timed out" in str(exc_info.value)
    
    @patch('core.llm_processor.subprocess.run')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_with_cursor_agent_clean_markdown(self, mock_is_available, mock_subprocess):
        # Mock CLI availability
        mock_is_available.return_value = True
        
        # Mock subprocess response with markdown
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "```sql\nSELECT * FROM users\n```"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        query_text = "Show all users"
        schema_info = {'tables': {}}
        
        result = generate_sql_with_cursor_agent(query_text, schema_info)
        
        assert result == "SELECT * FROM users"
    
    @patch('core.llm_processor.subprocess.run')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_with_claude_success(self, mock_is_available, mock_subprocess):
        # Mock CLI availability
        mock_is_available.return_value = True
        
        # Mock subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "SELECT * FROM products WHERE price < 100"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        query_text = "Show me products under $100"
        schema_info = {
            'tables': {
                'products': {
                    'columns': {'id': 'INTEGER', 'name': 'TEXT', 'price': 'REAL'},
                    'row_count': 50
                }
            }
        }
        
        result = generate_sql_with_claude(query_text, schema_info)
        
        assert result == "SELECT * FROM products WHERE price < 100"
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[0][0][0] == "claude"
        assert "-p" in call_args[0][0]
    
    @patch('core.llm_processor.shutil.which')
    def test_generate_sql_with_claude_not_available(self, mock_which):
        # Mock CLI not available
        mock_which.return_value = None
        
        query_text = "Show all products"
        schema_info = {'tables': {}}
        
        with pytest.raises(ValueError) as exc_info:
            generate_sql_with_claude(query_text, schema_info)
        
        assert "claude command not found" in str(exc_info.value)
    
    @patch('core.llm_processor.subprocess.run')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_with_claude_timeout(self, mock_is_available, mock_subprocess):
        # Mock CLI availability
        mock_is_available.return_value = True
        
        # Mock timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("claude", 60)
        
        query_text = "Show all products"
        schema_info = {'tables': {}}
        
        with pytest.raises(Exception) as exc_info:
            generate_sql_with_claude(query_text, schema_info)
        
        assert "timed out" in str(exc_info.value)
    
    @patch('core.llm_processor.generate_sql_with_cursor_agent')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_cursor_agent_provider(self, mock_is_available, mock_cursor_agent):
        # Test explicit cursor-agent provider
        mock_is_available.return_value = True
        mock_cursor_agent.return_value = "SELECT * FROM users"
        
        with patch.dict(os.environ, {}, clear=True):
            request = QueryRequest(query="Show all users", llm_provider="cursor-agent")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM users"
            mock_cursor_agent.assert_called_once_with("Show all users", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_claude')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_claude_provider(self, mock_is_available, mock_claude):
        # Test explicit claude provider
        mock_is_available.return_value = True
        mock_claude.return_value = "SELECT * FROM products"
        
        with patch.dict(os.environ, {}, clear=True):
            request = QueryRequest(query="Show all products", llm_provider="claude")
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM products"
            mock_claude.assert_called_once_with("Show all products", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_cursor_agent')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_cursor_agent_fallback(self, mock_is_available, mock_cursor_agent):
        # Test cursor-agent fallback when no API keys (uses default "openai" but falls back)
        def side_effect(cmd):
            return cmd == "cursor-agent"
        mock_is_available.side_effect = side_effect
        mock_cursor_agent.return_value = "SELECT * FROM orders"
        
        with patch.dict(os.environ, {}, clear=True):
            # Use default provider which will try OpenAI first, then fallback
            request = QueryRequest(query="Show all orders")  # Uses default "openai"
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM orders"
            mock_cursor_agent.assert_called_once_with("Show all orders", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_claude')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_claude_fallback(self, mock_is_available, mock_claude):
        # Test claude fallback when no API keys, cursor-agent not available
        def side_effect(cmd):
            if cmd == "cursor-agent":
                return False
            if cmd == "claude":
                return True
            return False
        mock_is_available.side_effect = side_effect
        mock_claude.return_value = "SELECT * FROM customers"
        
        with patch.dict(os.environ, {}, clear=True):
            # Use default provider which will try OpenAI first, then fallback
            request = QueryRequest(query="Show all customers")  # Uses default "openai"
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM customers"
            mock_claude.assert_called_once_with("Show all customers", schema_info)
    
    @patch('core.llm_processor.generate_sql_with_openai')
    @patch('core.llm_processor._is_cli_available')
    def test_generate_sql_env_provider_override(self, mock_is_available, mock_openai):
        # Test LLM_PROVIDER environment variable override
        mock_is_available.return_value = False
        mock_openai.return_value = "SELECT * FROM inventory"
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'openai'}, clear=True):
            request = QueryRequest(query="Show inventory", llm_provider="openai")  # Default
            schema_info = {'tables': {}}
            
            result = generate_sql(request, schema_info)
            
            assert result == "SELECT * FROM inventory"
            mock_openai.assert_called_once_with("Show inventory", schema_info)