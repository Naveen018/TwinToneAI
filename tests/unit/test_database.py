import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.db.database import DatabaseConnection, Prompt

class TestDatabaseConnection:
    """Test database connection and operations."""

    @patch('app.db.database.create_engine')
    @patch('app.db.database.sessionmaker')
    def test_database_initialization_success(self, mock_sessionmaker, mock_create_engine):
        """Test successful database initialization."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = MagicMock()
        mock_sessionmaker.return_value = mock_session_class
        
        db = DatabaseConnection()
        
        assert db.engine == mock_engine
        assert db.Session == mock_session_class
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)

    @patch('app.db.database.create_engine')
    def test_database_initialization_missing_credentials(self, mock_create_engine):
        """Test database initialization with missing credentials."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DatabaseConnection()
            
            assert "Database credentials not fully specified" in str(exc_info.value)

    @patch('app.db.database.create_engine')
    @patch('app.db.database.sessionmaker')
    def test_database_initialization_connection_error(self, mock_sessionmaker, mock_create_engine):
        """Test database initialization with connection error."""
        mock_create_engine.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            DatabaseConnection()
        
        assert "Connection failed" in str(exc_info.value)

class TestDatabaseOperations:
    """Test database CRUD operations."""

    @patch('app.db.database.create_engine')
    @patch('app.db.database.sessionmaker')
    def setup_method(self, method, mock_sessionmaker, mock_create_engine):
        """Setup method to create a mock database connection."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        self.mock_session = MagicMock()
        mock_session_class = MagicMock(return_value=self.mock_session)
        mock_sessionmaker.return_value = mock_session_class
        
        self.db = DatabaseConnection()

    def test_insert_prompt_success(self):
        """Test successful prompt insertion."""
        prompt_id = uuid4()
        user_id = "test_user"
        query = "What is AI?"
        casual_response = "AI is cool!"
        formal_response = "Artificial Intelligence is..."
        
        self.db.insert_prompt(prompt_id, user_id, query, casual_response, formal_response)
        
        # Verify session operations
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()
        
        # Verify the prompt object was created correctly
        added_prompt = self.mock_session.add.call_args[0][0]
        assert added_prompt.id == prompt_id
        assert added_prompt.user_id == user_id
        assert added_prompt.query == query
        assert added_prompt.casual_response == casual_response
        assert added_prompt.formal_response == formal_response

    def test_insert_prompt_database_error(self):
        """Test prompt insertion with database error."""
        self.mock_session.add.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(SQLAlchemyError):
            self.db.insert_prompt(uuid4(), "user", "query", "casual", "formal")
        
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_get_history_by_user_id_success(self):
        """Test successful history retrieval."""
        user_id = "test_user"
        limit = 10
        offset = 0
        
        # Mock query result
        mock_prompt1 = MagicMock()
        mock_prompt1.id = uuid4()
        mock_prompt1.user_id = user_id
        mock_prompt1.query = "Query 1"
        mock_prompt1.casual_response = "Casual 1"
        mock_prompt1.formal_response = "Formal 1"
        mock_prompt1.created_at = datetime.now()
        
        mock_prompt2 = MagicMock()
        mock_prompt2.id = uuid4()
        mock_prompt2.user_id = user_id
        mock_prompt2.query = "Query 2"
        mock_prompt2.casual_response = "Casual 2"
        mock_prompt2.formal_response = "Formal 2"
        mock_prompt2.created_at = datetime.now()
        
        mock_query = MagicMock()
        mock_query.__iter__ = lambda x: iter([mock_prompt1, mock_prompt2])
        
        # Setup mock session query chain
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset.return_value = mock_query
        
        result = self.db.get_history_by_user_id(user_id, limit, offset)
        
        assert len(result) == 2
        assert result[0]["user_id"] == user_id
        assert result[0]["query"] == "Query 1"
        assert result[1]["query"] == "Query 2"
        self.mock_session.close.assert_called_once()

    def test_get_history_by_user_id_database_error(self):
        """Test history retrieval with database error."""
        self.mock_session.query.side_effect = SQLAlchemyError("Query failed")
        
        with pytest.raises(SQLAlchemyError):
            self.db.get_history_by_user_id("user", 10, 0)
        
        self.mock_session.close.assert_called_once()

    def test_get_all_user_ids_success(self):
        """Test successful retrieval of all user IDs."""
        # Mock execute result
        mock_result = MagicMock()
        mock_result.__iter__ = lambda x: iter([("user1",), ("user2",), ("user3",)])
        self.mock_session.execute.return_value = mock_result
        
        result = self.db.get_all_user_ids()
        
        assert result == ["user1", "user2", "user3"]
        self.mock_session.execute.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_get_all_user_ids_database_error(self):
        """Test user IDs retrieval with database error."""
        self.mock_session.execute.side_effect = SQLAlchemyError("Execute failed")
        
        with pytest.raises(SQLAlchemyError):
            self.db.get_all_user_ids()
        
        self.mock_session.close.assert_called_once()

    def test_get_history_empty_result(self):
        """Test history retrieval with no results."""
        mock_query = MagicMock()
        mock_query.__iter__ = lambda x: iter([])
        
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset.return_value = mock_query
        
        result = self.db.get_history_by_user_id("nonexistent_user", 10, 0)
        
        assert result == []
        self.mock_session.close.assert_called_once()

    def test_get_history_with_pagination(self):
        """Test history retrieval with different pagination parameters."""
        user_id = "test_user"
        limit = 5
        offset = 10
        
        mock_query = MagicMock()
        mock_query.__iter__ = lambda x: iter([])
        
        query_chain = self.mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset
        query_chain.return_value = mock_query
        
        self.db.get_history_by_user_id(user_id, limit, offset)
        
        # Verify pagination parameters were used
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_with(limit)
        query_chain.assert_called_with(offset)