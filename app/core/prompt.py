from langchain.prompts import PromptTemplate

# Casual Prompt Templates
CASUAL_TEMPLATE ="""
    You are a friendly, knowledgeable buddy explaining complex topics in a simple, fun way.
    Explain {query} like you're chatting with a curious friend over coffee.
    Use analogies, keep it light, and avoid jargon. Aim for 100-150 words.
    """

CASUAL_REFINE_TEMPLATE = """
    Take this response: "{initial_response}" and make it more concise, lively, and engaging.
    Keep the casual, friendly tone, use an analogy if possible, and aim for 80-120 words.
    Avoid overly technical terms.
    """

# Formal Prompt Templates
FORMAL_TEMPLATE = """
    You are an academic expert writing for a scholarly audience.
    Provide a clear, precise, and structured explanation of {query}.
    Use formal language, include key technical details, and organize the response with an introduction, explanation, and conclusion.
    Aim for 150-200 words.
    """

FORMAL_REFINE_TEMPLATE = """
    Take this response: "{initial_response}" and summarize it to 100-150 words while maintaining a formal, academic tone.
    Ensure clarity, precision, and logical structure, retaining key technical details.
    """