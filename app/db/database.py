from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

Base = declarative_base()

class Prompt(Base):
    __tablename__ = 'conversation_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    casual_response = Column(Text)
    formal_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseConnection:
    def __init__(self):
        # Construct database URL from environment variables
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_host = os.getenv("POSTGRES_HOST", "localhost")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        db_name = os.getenv("POSTGRES_DB")
        
        if not all([db_user, db_password, db_name]):
            raise ValueError("Database credentials not fully specified in environment variables")
        
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        try:
            self.engine = create_engine(database_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database connection: %s", str(e))
            raise

    def insert_prompt(self, id, user_id, query, casual_response, formal_response):
        """
        Insert a new prompt and its responses into the database.
        """
        session = self.Session()
        try:
            prompt = Prompt(
                id=id,
                user_id=user_id,
                query=query,
                casual_response=casual_response,
                formal_response=formal_response
            )
            session.add(prompt)
            session.commit()
            logger.info("Inserted prompt for user_id: %s", user_id)
        except Exception as e:
            session.rollback()
            logger.error("Failed to insert prompt for user_id %s: %s", user_id, str(e))
            raise
        finally:
            session.close()

    def get_history_by_user_id(self, user_id: str, limit: int, offset: int) -> list:
        """
        Retrieve prompt history for a given user_id.
        """
        session = self.Session()
        try:
            query = session.query(Prompt).filter(Prompt.user_id == user_id).order_by(Prompt.created_at.desc()).limit(limit).offset(offset)
            history = [
                {
                    "id": str(prompt.id),
                    "user_id": prompt.user_id,
                    "query": prompt.query,
                    "casual_response": prompt.casual_response,
                    "formal_response": prompt.formal_response,
                    "created_at": prompt.created_at.isoformat()
                }
                for prompt in query
            ]
            logger.info("Retrieved %d history records for user_id: %s", len(history), user_id)
            return history
        except Exception as e:
            logger.error("Failed to retrieve history for user_id %s: %s", user_id, str(e))
            raise
        finally:
            session.close()

    def get_all_user_ids(self) -> list:
        """
        Retrieve all distinct user_ids from the conversation_history table.
        
        Returns:
            list: List of unique user_id strings.
        """
        session = self.Session()
        try:
            result = session.execute(text("SELECT DISTINCT user_id FROM conversation_history ORDER BY user_id"))
            user_ids = [row[0] for row in result]
            logger.info("Retrieved %d distinct user_ids", len(user_ids))
            return user_ids
        except Exception as e:
            logger.error("Failed to retrieve user_ids: %s", str(e))
            raise
        finally:
            session.close()