# TwinToneAI

TwinToneAI is a FastAPI-based application that generates both casual and formal responses to user queries using AI. The application features a Streamlit frontend for user interaction and a PostgreSQL database for storing conversation history.

## Features

- Dual-tone response generation (casual and formal)
- User conversation history tracking
- Modern Streamlit-based user interface
- RESTful API endpoints
- PostgreSQL database integration
- Docker support for easy deployment

## Prerequisites

- Python 3.8+
- PostgreSQL
- OpenAI API key (for response generation)
- Docker and Docker Compose (for containerized deployment)

## Project Structure

```
TwinToneAI/
├── app/
│   ├── backend/         # FastAPI application
│   ├── frontend/        # Streamlit interface
│   ├── core/           # Core business logic
│   └── db/             # Database models and connection
├── .env.example        # Environment variables template
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile         # Docker configuration
└── requirements.txt    # Python dependencies
```

## Setup Instructions

### Option 1: Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TwinToneAI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your configuration values:
   - Database credentials
   - OpenAI API key
   - Other configuration settings

5. **Set up PostgreSQL database**
   - Create a new database named `twintoneai_db`
   - Ensure PostgreSQL is running
   - Update database credentials in `.env` if different from defaults

### Option 2: Docker Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TwinToneAI
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your configuration values

3. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

## Running the Application

### Option 1: Local Run

1. **Start the FastAPI backend**
   ```bash
   uvicorn app.backend.app:app --reload
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Streamlit frontend**
   ```bash
   streamlit run app/frontend/streamlit.py
   ```
   The frontend will be available at `http://localhost:8001`

### Option 2: Docker Run

1. **Start all services**
   ```bash
   docker-compose up
   ```
   This will start:
   - FastAPI backend at `http://localhost:8000`
   - Streamlit frontend at `http://localhost:8001`
   - PostgreSQL database

2. **Run in detached mode**
   ```bash
   docker-compose up -d
   ```

3. **Stop the services**
   ```bash
   docker-compose down
   ```

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

## API Endpoints

- `POST /generate`: Generate casual and formal responses
  ```json
  {
    "query": "What is artificial intelligence?",
    "user_id": "user123"
  }
  ```

- `GET /history/{user_id}`: Get user's conversation history
  - Query parameters: `limit` (default: 10), `offset` (default: 0)

- `GET /users`: Get list of all users

## Environment Variables

Required environment variables in `.env`:
```
# Database Configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=twintoneai_db

# API Configuration
API_BASE_URL=http://localhost:8000

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- The application uses FastAPI for the backend and Streamlit for the frontend
- Database migrations are handled automatically on startup

## Contact

For any questions or support, please reach out to [naveenv3112000@gmail.com](mailto:naveenv3112000@gmail.com)

## License

[Your License Here]
