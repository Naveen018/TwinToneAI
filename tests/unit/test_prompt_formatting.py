import pytest
from langchain.prompts import PromptTemplate
from app.core.prompt import CASUAL_TEMPLATE, FORMAL_TEMPLATE, CASUAL_REFINE_TEMPLATE, FORMAL_REFINE_TEMPLATE

class TestPromptFormatting:
    """Test prompt template formatting and validation."""

    def test_casual_template_formatting(self):
        """Test that casual template formats correctly with query input."""
        prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        test_query = "What is quantum computing?"
        
        formatted_prompt = prompt.format(query=test_query)
        
        assert test_query in formatted_prompt
        assert "friendly" in formatted_prompt.lower() or "buddy" in formatted_prompt.lower()
        assert "100-150 words" in formatted_prompt

    def test_formal_template_formatting(self):
        """Test that formal template formats correctly with query input."""
        prompt = PromptTemplate(template=FORMAL_TEMPLATE, input_variables=["query"])
        test_query = "What is quantum computing?"
        
        formatted_prompt = prompt.format(query=test_query)
        
        assert test_query in formatted_prompt
        assert "academic" in formatted_prompt.lower() or "formal" in formatted_prompt.lower()
        assert "150-200 words" in formatted_prompt

    def test_casual_refine_template_formatting(self):
        """Test that casual refine template formats correctly."""
        prompt = PromptTemplate(template=CASUAL_REFINE_TEMPLATE, input_variables=["initial_response"])
        test_response = "This is a test response that needs refinement."
        
        formatted_prompt = prompt.format(initial_response=test_response)
        
        assert test_response in formatted_prompt
        assert "casual" in formatted_prompt.lower()
        assert "80-120 words" in formatted_prompt

    def test_formal_refine_template_formatting(self):
        """Test that formal refine template formats correctly."""
        prompt = PromptTemplate(template=FORMAL_REFINE_TEMPLATE, input_variables=["initial_response"])
        test_response = "This is a test response that needs refinement."
        
        formatted_prompt = prompt.format(initial_response=test_response)
        
        assert test_response in formatted_prompt
        assert "formal" in formatted_prompt.lower()
        assert "100-150 words" in formatted_prompt

    def test_template_input_variables(self):
        """Test that templates have correct input variables."""
        casual_prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        formal_prompt = PromptTemplate(template=FORMAL_TEMPLATE, input_variables=["query"])
        
        assert casual_prompt.input_variables == ["query"]
        assert formal_prompt.input_variables == ["query"]

    def test_template_content_requirements(self):
        """Test that templates contain required content guidelines."""
        # Test casual template requirements
        assert "friendly" in CASUAL_TEMPLATE.lower() or "buddy" in CASUAL_TEMPLATE.lower()
        assert "analogi" in CASUAL_TEMPLATE.lower()  # analogies
        assert "jargon" in CASUAL_TEMPLATE.lower()
        
        # Test formal template requirements
        assert "academic" in FORMAL_TEMPLATE.lower() or "formal" in FORMAL_TEMPLATE.lower()
        assert "technical" in FORMAL_TEMPLATE.lower()
        assert "structure" in FORMAL_TEMPLATE.lower()

    @pytest.mark.parametrize("query", [
        "What is artificial intelligence?",
        "Explain blockchain technology",
        "How does photosynthesis work?",
        "What are the benefits of renewable energy?"
    ])
    def test_template_with_various_queries(self, query):
        """Test templates work with various types of queries."""
        casual_prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        formal_prompt = PromptTemplate(template=FORMAL_TEMPLATE, input_variables=["query"])
        
        casual_formatted = casual_prompt.format(query=query)
        formal_formatted = formal_prompt.format(query=query)
        
        assert query in casual_formatted
        assert query in formal_formatted
        assert len(casual_formatted) > len(CASUAL_TEMPLATE)
        assert len(formal_formatted) > len(FORMAL_TEMPLATE)

    def test_empty_query_handling(self):
        """Test how templates handle empty queries."""
        prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        
        formatted_prompt = prompt.format(query="")
        
        # Should still format without error
        assert isinstance(formatted_prompt, str)
        assert len(formatted_prompt) > 0

    def test_special_characters_in_query(self):
        """Test templates handle special characters in queries."""
        special_query = "What is AI? How does it work & why is it important?"
        prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        
        formatted_prompt = prompt.format(query=special_query)
        
        assert special_query in formatted_prompt
        assert len(formatted_prompt) > len(CASUAL_TEMPLATE)