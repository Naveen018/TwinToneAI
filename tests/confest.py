import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from uuid import uuid4

# Import your app components
from app.backend import app
from app.db.database import Base, DatabaseConnection
from app.core.generate_response import generate_responses

# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_db_connection():
    """Mock database connection for unit tests."""
    mock_db = MagicMock(spec=DatabaseConnection)
    mock_db.insert_prompt = MagicMock()
    mock_db.get_history_by_user_id = MagicMock()
    mock_db.get_all_user_ids = MagicMock()
    return mock_db

@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test_user_123"

@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "Explain artificial intelligence"

@pytest.fixture
def sample_responses():
    """Sample AI responses for testing."""
    return {
        "casual_response": "AI is like having a really smart assistant that can think and learn, helping us solve problems and make decisions. It's everywhere from your phone's voice assistant to recommendation systems!",
        "formal_response": "Artificial Intelligence refers to the simulation of human intelligence processes by machines, particularly computer systems. These processes include learning, reasoning, and self-correction."
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response object."""
    class MockResponse:
        def __init__(self, content):
            self.content = content
    return MockResponse

@pytest.fixture
def sample_history_data():
    """Sample history data for testing."""
    return [
        {
            "id": str(uuid4()),
            "user_id": "test_user_123",
            "query": "What is machine learning?",
            "casual_response": "Machine learning is like teaching computers to learn patterns, just like how you learn to recognize faces!",
            "formal_response": "Machine learning is a subset of artificial intelligence that enables systems to automatically learn and improve from experience.",
            "created_at": "2024-01-01T12:00:00"
        },
        {
            "id": str(uuid4()),
            "user_id": "test_user_123", 
            "query": "Explain blockchain",
            "casual_response": "Blockchain is like a digital ledger that everyone can see but no one can cheat on!",
            "formal_response": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records, secured using cryptography.",
            "created_at": "2024-01-01T11:00:00"
        }
    ]

@pytest.fixture
def mock_generate_responses():
    """Mock the generate_responses function."""
    async def _mock_generate_responses(query: str, user_id: str):
        return {
            "casual_response": f"Casual response for: {query}",
            "formal_response": f"Formal response for: {query}"
        }
    return _mock_generate_responses

# Environment variable mocks
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "test_db")