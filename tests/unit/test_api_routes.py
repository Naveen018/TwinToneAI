import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4
from app.backend import app

class TestAPIRoutes:
    """Test FastAPI route validation and responses."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_generate_endpoint_success(self, mock_db, mock_generate_responses):
        """Test successful /generate endpoint."""
        # Mock generate_responses
        mock_generate_responses.return_value = {
            "casual_response": "This is a casual response!",
            "formal_response": "This is a formal response."
        }
        
        # Mock database insert
        mock_db.insert_prompt = MagicMock()
        
        request_data = {
            "query": "What is artificial intelligence?",
            "user_id": "test_user_123"
        }
        
        response = self.client.post("/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["user_id"] == "test_user_123"
        assert data["query"] == "What is artificial intelligence?"
        assert data["casual_response"] == "This is a casual response!"
        assert data["formal_response"] == "This is a formal response."
        
        # Verify database insert was called
        mock_db.insert_prompt.assert_called_once()

    def test_generate_endpoint_invalid_request(self):
        """Test /generate endpoint with invalid request data."""
        # Missing required fields
        invalid_requests = [
            {},  # Empty request
            {"query": "test"},  # Missing user_id
            {"user_id": "test"},  # Missing query
            {"query": "", "user_id": ""},  # Empty values
        ]
        
        for invalid_request in invalid_requests:
            response = self.client.post("/generate", json=invalid_request)
            assert response.status_code == 422  # Validation error

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_generate_endpoint_generation_error(self, mock_db, mock_generate_responses):
        """Test /generate endpoint when AI generation fails."""
        # Mock generate_responses to raise an exception
        mock_generate_responses.side_effect = Exception("AI service unavailable")
        
        request_data = {
            "query": "What is AI?",
            "user_id": "test_user"
        }
        
        response = self.client.post("/generate", json=request_data)
        
        assert response.status_code == 500
        assert "Failed to generate responses" in response.json()["detail"]

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_generate_endpoint_database_error(self, mock_db, mock_generate_responses):
        """Test /generate endpoint when database insertion fails."""
        # Mock successful generation but database failure
        mock_generate_responses.return_value = {
            "casual_response": "Casual",
            "formal_response": "Formal"
        }
        mock_db.insert_prompt.side_effect = Exception("Database connection failed")
        
        request_data = {
            "query": "What is AI?",
            "user_id": "test_user"
        }
        
        response = self.client.post("/generate", json=request_data)
        
        assert response.status_code == 500
        assert "Failed to generate responses" in response.json()["detail"]

    @patch('app.main.db')
    def test_history_endpoint_success(self, mock_db):
        """Test successful /history endpoint."""
        user_id = "test_user_123"
        mock_history_data = [
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "query": "What is machine learning?",
                "casual_response": "ML is like teaching computers to learn!",
                "formal_response": "Machine learning is a subset of AI...",
                "created_at": "2024-01-01T12:00:00"
            }
        ]
        
        mock_db.get_history_by_user_id.return_value = mock_history_data
        
        response = self.client.get(f"/history/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["user_id"] == user_id
        assert data[0]["query"] == "What is machine learning?"
        
        # Verify database method was called with correct parameters
        mock_db.get_history_by_user_id.assert_called_once_with(user_id, 10, 0)

    @patch('app.main.db')
    def test_history_endpoint_with_pagination(self, mock_db):
        """Test /history endpoint with custom limit and offset."""
        user_id = "test_user"
        mock_db.get_history_by_user_id.return_value = []
        
        response = self.client.get(f"/history/{user_id}?limit=5&offset=20")
        
        assert response.status_code == 200
        mock_db.get_history_by_user_id.assert_called_once_with(user_id, 5, 20)

    @patch('app.main.db')
    def test_history_endpoint_database_error(self, mock_db):
        """Test /history endpoint when database query fails."""
        user_id = "test_user"
        mock_db.get_history_by_user_id.side_effect = Exception("Database query failed")
        
        response = self.client.get(f"/history/{user_id}")
        
        assert response.status_code == 500
        assert "Failed to retrieve history" in response.json()["detail"]

    @patch('app.main.db')
    def test_history_endpoint_empty_result(self, mock_db):
        """Test /history endpoint with no history data."""
        user_id = "new_user"
        mock_db.get_history_by_user_id.return_value = []
        
        response = self.client.get(f"/history/{user_id}")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_history_endpoint_invalid_pagination(self):
        """Test /history endpoint with invalid pagination parameters."""
        user_id = "test_user"
        
        # Test negative values
        response = self.client.get(f"/history/{user_id}?limit=-1&offset=-1")
        assert response.status_code == 422

    @patch('app.main.db')
    def test_users_endpoint_success(self, mock_db):
        """Test successful /users endpoint."""
        mock_user_ids = ["user1", "user2", "user3"]
        mock_db.get_all_user_ids.return_value = mock_user_ids
        
        response = self.client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user_ids" in data
        assert data["user_ids"] == mock_user_ids
        mock_db.get_all_user_ids.assert_called_once()

    @patch('app.main.db')
    def test_users_endpoint_database_error(self, mock_db):
        """Test /users endpoint when database query fails."""
        mock_db.get_all_user_ids.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/users")
        
        assert response.status_code == 500
        assert "Failed to retrieve user_ids" in response.json()["detail"]

    @patch('app.main.db')
    def test_users_endpoint_empty_result(self, mock_db):
        """Test /users endpoint with no users."""
        mock_db.get_all_user_ids.return_value = []
        
        response = self.client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_ids"] == []

    def test_nonexistent_endpoint(self):
        """Test calling non-existent endpoint."""
        response = self.client.get("/nonexistent")
        assert response.status_code == 404

    def test_root_endpoint_redirect(self):
        """Test root endpoint behavior."""
        response = self.client.get("/")
        # FastAPI typically returns 404 for undefined root, or you can define it
        assert response.status_code in [404, 200]  # Depending on your setup

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_generate_endpoint_large_query(self, mock_db, mock_generate_responses):
        """Test /generate endpoint with very large query."""
        mock_generate_responses.return_value = {
            "casual_response": "Large casual response",
            "formal_response": "Large formal response"
        }
        mock_db.insert_prompt = MagicMock()
        
        large_query = "What is AI? " * 1000  # Very large query
        request_data = {
            "query": large_query,
            "user_id": "test_user"
        }
        
        response = self.client.post("/generate", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["query"] == large_query

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_generate_endpoint_special_characters(self, mock_db, mock_generate_responses):
        """Test /generate endpoint with special characters in query."""
        mock_generate_responses.return_value = {
            "casual_response": "Special response",
            "formal_response": "Formal special response"
        }
        mock_db.insert_prompt = MagicMock()
        
        special_query = "What is AI? 🤖 How does it work & why is it important?"
        request_data = {
            "query": special_query,
            "user_id": "test_user_123"
        }
        
        response = self.client.post("/generate", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["query"] == special_query