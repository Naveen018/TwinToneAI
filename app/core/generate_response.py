import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from app.core.prompt import CASUAL_TEMPLATE, CASUAL_REFINE_TEMPLATE, FORMAL_TEMPLATE, FORMAL_REFINE_TEMPLATE

async def generate_responses(query: str, user_id: str) -> dict:
    """
    Generate casual and formal responses for a given query using LangChain.

    Args:
        query (str): User query.
        user_id (str): User identifier.

    Returns:
        dict: Dictionary containing casual and formal responses.
    """
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

        # Casual response
        casual_prompt = PromptTemplate(template=CASUAL_TEMPLATE, input_variables=["query"])
        casual_chain = casual_prompt | llm
        casual_response = (await casual_chain.ainvoke({"query": query})).content

        # Formal response
        formal_prompt = PromptTemplate(template=FORMAL_TEMPLATE, input_variables=["query"])
        formal_chain = formal_prompt | llm
        formal_response = (await formal_chain.ainvoke({"query": query})).content

        return {
            "casual_response": casual_response,
            "formal_response": formal_response
        }
    except Exception as e:
        raise Exception(f"Failed to generate responses: {str(e)}")