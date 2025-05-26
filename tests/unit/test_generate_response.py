import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.generate_response import generate_responses

class TestGenerateResponse:
    """Test AI generation logic with mocked responses."""

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_success(self, mock_chat_openai):
        """Test successful generation of casual and formal responses."""
        # Mock the LLM and its responses
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock casual response
        casual_mock_response = MagicMock()
        casual_mock_response.content = "This is a casual response about the query!"
        
        # Mock formal response  
        formal_mock_response = MagicMock()
        formal_mock_response.content = "This is a formal, academic response regarding the query."
        
        # Configure the mock to return different responses for different calls
        mock_llm.ainvoke = AsyncMock(side_effect=[casual_mock_response, formal_mock_response])
        
        # Test the function
        query = "What is machine learning?"
        user_id = "test_user"
        
        result = await generate_responses(query, user_id)
        
        # Assertions
        assert isinstance(result, dict)
        assert "casual_response" in result
        assert "formal_response" in result
        assert result["casual_response"] == "This is a casual response about the query!"
        assert result["formal_response"] == "This is a formal, academic response regarding the query."
        
        # Verify LLM was called twice (once for each style)
        assert mock_llm.ainvoke.call_count == 2

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_with_different_queries(self, mock_chat_openai):
        """Test generation with different types of queries."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        queries = [
            "What is artificial intelligence?",
            "Explain quantum computing",
            "How does photosynthesis work?"
        ]
        
        for i, query in enumerate(queries):
            # Mock responses for each query
            casual_response = MagicMock()
            casual_response.content = f"Casual response {i+1}"
            formal_response = MagicMock()
            formal_response.content = f"Formal response {i+1}"
            
            mock_llm.ainvoke = AsyncMock(side_effect=[casual_response, formal_response])
            
            result = await generate_responses(query, "test_user")
            
            assert result["casual_response"] == f"Casual response {i+1}"
            assert result["formal_response"] == f"Formal response {i+1}"

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_llm_initialization(self, mock_chat_openai):
        """Test that LLM is initialized with correct parameters."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock responses
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        await generate_responses("test query", "test_user")
        
        # Verify ChatOpenAI was initialized with correct parameters
        mock_chat_openai.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="test-api-key"  # From conftest.py mock
        )

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_prompt_templates_used(self, mock_chat_openai):
        """Test that correct prompt templates are used."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        query = "Test query"
        await generate_responses(query, "test_user")
        
        # Verify ainvoke was called twice (casual and formal)
        assert mock_llm.ainvoke.call_count == 2
        
        # Check that the query was passed to both calls
        calls = mock_llm.ainvoke.call_args_list
        assert calls[0][0][0]["query"] == query  # Casual prompt call
        assert calls[1][0][0]["query"] == query  # Formal prompt call

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_exception_handling(self, mock_chat_openai):
        """Test exception handling when LLM calls fail."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock LLM to raise an exception
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception) as exc_info:
            await generate_responses("test query", "test_user")
        
        assert "Failed to generate responses" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_empty_query(self, mock_chat_openai):
        """Test handling of empty queries."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_response = MagicMock()
        mock_response.content = "Response to empty query"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        result = await generate_responses("", "test_user")
        
        assert isinstance(result, dict)
        assert "casual_response" in result
        assert "formal_response" in result

    @pytest.mark.asyncio
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_long_query(self, mock_chat_openai):
        """Test handling of very long queries."""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        mock_response = MagicMock()
        mock_response.content = "Response to long query"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        long_query = "What is artificial intelligence? " * 100  # Very long query
        result = await generate_responses(long_query, "test_user")
        
        assert isinstance(result, dict)
        assert len(result["casual_response"]) > 0
        assert len(result["formal_response"]) > 0

    @pytest.mark.asyncio 
    @patch('app.core.generate_response.os.getenv')
    @patch('app.core.generate_response.ChatOpenAI')
    async def test_generate_responses_missing_api_key(self, mock_chat_openai, mock_getenv):
        """Test handling when OpenAI API key is missing."""
        # Mock missing API key
        mock_getenv.return_value = None  
        mock_chat_openai.side_effect = Exception("API key not provided")
        
        with pytest.raises(Exception) as exc_info:
            await generate_responses("test query", "test_user")
        
        assert "Failed to generate responses" in str(exc_info.value)