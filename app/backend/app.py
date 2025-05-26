from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from app.core.generate_response import generate_responses
from app.db.database import DatabaseConnection
from typing import List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="TwinToneAI Response Generation")

# Pydantic models for request and response validation
class PromptRequest(BaseModel):
    query: str
    user_id: str

class PromptResponse(BaseModel):
    id: UUID
    user_id: str
    query: str
    casual_response: str
    formal_response: str

class HistoryResponse(BaseModel):
    id: UUID
    user_id: str
    query: str
    casual_response: str
    formal_response: str
    created_at: datetime

class UserListResponse(BaseModel):
    user_ids: List[str]

# Database instance
db = DatabaseConnection()

@app.post("/generate", response_model=PromptResponse)
async def generate_response(request: PromptRequest):
    """
    Generate casual and formal responses for a user query and store in database.
    
    Args:
        request (PromptRequest): Contains query and user_id.
    
    Returns:
        PromptResponse: Contains UUID, user_id, query, and responses.
    """
    try:
        logger.info("Processing /generate for user_id: %s, query: %s", request.user_id, request.query)
        # Generate responses using LangChain
        responses = await generate_responses(request.query, request.user_id)
        prompt_id = uuid4()  # Generate unique ID for the database record
        
        # Store in database
        db.insert_prompt(
            id=prompt_id,
            user_id=request.user_id,
            query=request.query,
            casual_response=responses["casual_response"],
            formal_response=responses["formal_response"]
        )
        
        logger.info("Completed /generate for user_id: %s", request.user_id)
        return PromptResponse(
            id=prompt_id,
            user_id=request.user_id,
            query=request.query,
            casual_response=responses["casual_response"],
            formal_response=responses["formal_response"]
        )
    except Exception as e:
        logger.error("Error in /generate for user_id: %s: %s", request.user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate responses: {str(e)}")

@app.get("/history/{user_id}", response_model=List[HistoryResponse])
async def get_history(user_id: str, limit: int = 10, offset: int = 0):
    """
    Retrieve the history of queries and responses for a given user.
    
    Args:
        user_id (str): Unique identifier for the user.
        limit (int): Number of records to return (default: 10).
        offset (int): Number of records to skip (default: 0).
    
    Returns:
        List[HistoryResponse]: List of user queries and responses.
    """
    try:
        logger.info("Fetching history for user_id: %s", user_id)
        history = db.get_history_by_user_id(user_id, limit, offset)
        logger.info("Retrieved %d history records for user_id: %s", len(history), user_id)
        return [HistoryResponse(**record) for record in history]
    except Exception as e:
        logger.error("Error fetching history for user_id: %s: %s", user_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/users", response_model=UserListResponse)
async def get_users():
    """
    Retrieve all distinct user_ids from the conversation_history table.
    
    Returns:
        UserListResponse: List of unique user_ids.
    """
    try:
        logger.info("Fetching all user_ids")
        user_ids = db.get_all_user_ids()
        logger.info("Retrieved %d user_ids", len(user_ids))
        return UserListResponse(user_ids=user_ids)
    except Exception as e:
        logger.error("Error fetching user_ids: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user_ids: {str(e)}")