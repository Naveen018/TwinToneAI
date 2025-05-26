import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

def get_llm():
    """
    Initialize and return the configured LLM (gpt-4o-mini).
    
    Returns:
        ChatOpenAI: Configured LangChain LLM instance.
    """
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7  # Default temperature, can be overridden
    )