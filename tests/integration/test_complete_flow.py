import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4
from app.backend import app

class TestCompleteFlow:
    """Integration tests that simulate complete user flows."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_complete_user_journey(self, mock_db, mock_generate_responses):
        """Test complete flow: generate -> store -> retrieve history."""
        user_id = "integration_test_user"
        
        # Step 1: Generate first query
        mock_generate_responses.return_value = {
            "casual_response": "AI is super cool technology!",
            "formal_response": "Artificial Intelligence refers to machine intelligence."
        }
        mock_db.insert_prompt = MagicMock()
        
        first_request = {
            "query": "What is artificial intelligence?",
            "user_id": user_id
        }
        
        response1 = self.client.post("/generate", json=first_request)
        assert response1.status_code == 200
        first_data = response1.json()
        
        # Step 2: Generate second query
        mock_generate_responses.return_value = {
            "casual_response": "ML is like teaching computers to learn patterns!",
            "formal_response": "Machine Learning is a subset of AI that enables systems to learn."
        }
        
        second_request = {
            "query": "Explain machine learning",
            "user_id": user_id
        }
        
        response2 = self.client.post("/generate", json=second_request)
        assert response2.status_code == 200
        second_data = response2.json()
        
        # Step 3: Retrieve history
        mock_history = [
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "query": "Explain machine learning",
                "casual_response": "ML is like teaching computers to learn patterns!",
                "formal_response": "Machine Learning is a subset of AI that enables systems to learn.",
                "created_at": "2024-01-01T12:30:00"
            },
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "query": "What is artificial intelligence?",
                "casual_response": "AI is super cool technology!",
                "formal_response": "Artificial Intelligence refers to machine intelligence.",
                "created_at": "2024-01-01T12:00:00"
            }
        ]
        mock_db.get_history_by_user_id.return_value = mock_history
        
        history_response = self.client.get(f"/history/{user_id}")
        assert history_response.status_code == 200
        history_data = history_response.json()
        
        # Verify complete flow
        assert len(history_data) == 2
        assert history_data[0]["query"] == "Explain machine learning"  # Most recent first
        assert history_data[1]["query"] == "What is artificial intelligence?"
        
        # Verify database operations were called
        assert mock_db.insert_prompt.call_count == 2
        mock_db.get_history_by_user_id.assert_called_once_with(user_id, 10, 0)

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_multiple_users_flow(self, mock_db, mock_generate_responses):
        """Test flow with multiple users to ensure data isolation."""
        user1_id = "user1"
        user2_id = "user2"
        
        # User 1 generates a query
        mock_generate_responses.return_value = {
            "casual_response": "User 1 casual response",
            "formal_response": "User 1 formal response"
        }
        mock_db.insert_prompt = MagicMock()
        
        user1_request = {
            "query": "User 1 query",
            "user_id": user1_id
        }
        
        response1 = self.client.post("/generate", json=user1_request)
        assert response1.status_code == 200
        assert response1.json()["user_id"] == user1_id
        
        # User 2 generates a query
        mock_generate_responses.return_value = {
            "casual_response": "User 2 casual response",
            "formal_response": "User 2 formal response"
        }
        
        user2_request = {
            "query": "User 2 query",
            "user_id": user2_id
        }
        
        response2 = self.client.post("/generate", json=user2_request)
        assert response2.status_code == 200
        assert response2.json()["user_id"] == user2_id
        
        # Get User 1 history
        mock_db.get_history_by_user_id.return_value = [{
            "id": str(uuid4()),
            "user_id": user1_id,
            "query": "User 1 query",
            "casual_response": "User 1 casual response",
            "formal_response": "User 1 formal response",
            "created_at": "2024-01-01T12:00:00"
        }]
        
        user1_history = self.client.get(f"/history/{user1_id}")
        assert user1_history.status_code == 200
        user1_data = user1_history.json()
        assert len(user1_data) == 1
        assert user1_data[0]["user_id"] == user1_id
        
        # Get User 2 history
        mock_db.get_history_by_user_id.return_value = [{
            "id": str(uuid4()),
            "user_id": user2_id,
            "query": "User 2 query",
            "casual_response": "User 2 casual response",
            "formal_response": "User 2 formal response",
            "created_at": "2024-01-01T12:00:00"
        }]
        
        user2_history = self.client.get(f"/history/{user2_id}")
        assert user2_history.status_code == 200
        user2_data = user2_history.json()
        assert len(user2_data) == 1
        assert user2_data[0]["user_id"] == user2_id
        
        # Verify users list includes both
        mock_db.get_all_user_ids.return_value = [user1_id, user2_id]
        users_response = self.client.get("/users")
        assert users_response.status_code == 200
        users_data = users_response.json()
        assert user1_id in users_data["user_ids"]
        assert user2_id in users_data["user_ids"]

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_error_recovery_flow(self, mock_db, mock_generate_responses):
        """Test system behavior during partial failures."""
        user_id = "error_test_user"
        
        # First request succeeds
        mock_generate_responses.return_value = {
            "casual_response": "Success response",
            "formal_response": "Success formal response"
        }
        mock_db.insert_prompt = MagicMock()
        
        success_request = {
            "query": "Successful query",
            "user_id": user_id
        }
        
        response1 = self.client.post("/generate", json=success_request)
        assert response1.status_code == 200
        
        # Second request fails during generation
        mock_generate_responses.side_effect = Exception("AI service down")
        
        failed_request = {
            "query": "Failed query", 
            "user_id": user_id
        }
        
        response2 = self.client.post("/generate", json=failed_request)
        assert response2.status_code == 500
        
        # History should still work and show only successful entries
        mock_db.get_history_by_user_id.return_value = [{
            "id": str(uuid4()),
            "user_id": user_id,
            "query": "Successful query",
            "casual_response": "Success response",
            "formal_response": "Success formal response",
            "created_at": "2024-01-01T12:00:00"
        }]
        
        history_response = self.client.get(f"/history/{user_id}")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data) == 1
        assert history_data[0]["query"] == "Successful query"

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_pagination_flow(self, mock_db, mock_generate_responses):
        """Test history retrieval with pagination."""
        user_id = "pagination_test_user"
        
        # Generate multiple queries (simulated)
        mock_generate_responses.return_value = {
            "casual_response": "Test response",
            "formal_response": "Test formal response"
        }
        mock_db.insert_prompt = MagicMock()
        
        # Simulate multiple generations
        for i in range(5):
            request = {
                "query": f"Query {i+1}",
                "user_id": user_id
            }
            response = self.client.post("/generate", json=request)
            assert response.status_code == 200
        
        # Test first page
        mock_history_page1 = [
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "query": f"Query {i}",
                "casual_response": "Test response",
                "formal_response": "Test formal response",
                "created_at": f"2024-01-01T12:{i:02d}:00"
            }
            for i in range(5, 3, -1)  # Most recent first
        ]
        mock_db.get_history_by_user_id.return_value = mock_history_page1
        
        page1_response = self.client.get(f"/history/{user_id}?limit=2&offset=0")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data) == 2
        
        # Test second page
        mock_history_page2 = [
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "query": f"Query {i}",
                "casual_response": "Test response",
                "formal_response": "Test formal response",
                "created_at": f"2024-01-01T12:{i:02d}:00"
            }
            for i in range(3, 1, -1)
        ]
        mock_db.get_history_by_user_id.return_value = mock_history_page2
        
        page2_response = self.client.get(f"/history/{user_id}?limit=2&offset=2")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert len(page2_data) == 2
        
        # Verify different pages have different data
        assert page1_data != page2_data

    @patch('app.main.generate_responses')
    @patch('app.main.db')
    def test_concurrent_requests_simulation(self, mock_db, mock_generate_responses):
        """Test behavior with rapid sequential requests (simulating concurrency)."""
        user_id = "concurrent_test_user"
        
        mock_generate_responses.return_value = {
            "casual_response": "Concurrent response",
            "formal_response": "Concurrent formal response"
        }
        mock_db.insert_prompt = MagicMock()
        
        # Rapid sequential requests
        responses = []
        for i in range(3):
            request = {
                "query": f"Concurrent query {i+1}",
                "user_id": user_id
            }
            response = self.client.post("/generate", json=request)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # All should have unique IDs
        response_ids = [r.json()["id"] for r in responses]
        assert len(set(response_ids)) == 3  # All unique
        
        # Database should have been called for each request
        assert mock_db.insert_prompt.call_count == 3