"""Sample data fixtures for testing."""

from uuid import uuid4
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Sample queries for testing
SAMPLE_QUERIES = [
    "What is artificial intelligence?",
    "Explain machine learning",
    "How does blockchain work?",
    "What are the benefits of renewable energy?",
    "Describe quantum computing",
    "How does photosynthesis work?",
    "What is climate change?",
    "Explain the theory of relativity",
    "How do neural networks function?",
    "What is sustainable development?",
    "What is cloud computing?",
    "How does cryptocurrency work?",
    "Explain data science",
    "What is cybersecurity?",
    "How do satellites work?"
]

# Sample casual responses
SAMPLE_CASUAL_RESPONSES = [
    "AI is like having a super smart assistant that can think and learn! It's everywhere from your phone's voice assistant to Netflix recommendations.",
    "Machine learning is basically teaching computers to spot patterns and make predictions, kind of like how you learn to recognize your friends' faces!",
    "Think of blockchain as a digital ledger that everyone can see but no one can cheat on - it's like having a transparent, tamper-proof record book!",
    "Renewable energy is like nature's way of powering our world - sun, wind, and water doing the heavy lifting instead of dirty fossil fuels!",
    "Quantum computing is mind-blowing! Imagine a computer that can be in multiple states at once, solving problems regular computers would take forever to crack.",
    "Photosynthesis is basically how plants eat sunlight! They take in CO2 and water, add some sunshine, and boom - they make their own food and give us oxygen.",
    "Climate change is like Earth having a fever - things are heating up because we've been pumping too much CO2 into the atmosphere.",
    "Einstein's relativity is wild - basically time and space are like a stretchy fabric that bends around massive objects. The faster you go, the slower time gets!",
    "Neural networks are inspired by how our brains work - lots of simple connections that together can recognize patterns and make smart decisions.",
    "Sustainable development is about meeting our needs today without screwing over future generations - it's like being a good roommate with planet Earth!"
]

# Sample formal responses
SAMPLE_FORMAL_RESPONSES = [
    "Artificial Intelligence refers to the simulation of human intelligence processes by machines, particularly computer systems, encompassing learning, reasoning, and self-correction capabilities.",
    "Machine Learning is a subset of artificial intelligence that enables systems to automatically learn and improve from experience without being explicitly programmed for each specific task.",
    "Blockchain technology is a distributed ledger system that maintains a continuously growing list of records, secured using cryptographic principles and consensus mechanisms.",
    "Renewable energy encompasses energy sources that are naturally replenished, including solar, wind, hydroelectric, and geothermal power, offering sustainable alternatives to fossil fuels.",
    "Quantum computing leverages quantum mechanical phenomena such as superposition and entanglement to process information in ways that classical computers cannot achieve.",
    "Photosynthesis is the biological process by which plants convert light energy, typically from the sun, into chemical energy stored in glucose molecules through the combination of carbon dioxide and water.",
    "Climate change refers to long-term shifts in global temperatures and weather patterns, primarily driven by human activities that increase atmospheric concentrations of greenhouse gases.",
    "Einstein's theory of relativity consists of special and general relativity, describing the relationship between space, time, gravity, and the fundamental structure of spacetime.",
    "Neural networks are computational models inspired by biological neural networks, consisting of interconnected nodes that process and transmit information through weighted connections.",
    "Sustainable development is a development approach that meets present needs while preserving the ability of future generations to meet their own needs through balanced economic, social, and environmental considerations."
]

def generate_sample_user_ids(count: int = 5) -> list:
    """Generate sample user IDs for testing."""
    return [f"test_user_{i+1}" for i in range(count)]

def generate_sample_prompt_data(user_id: str = None, count: int = 1) -> list:
    """Generate sample prompt data for testing."""
    if user_id is None:
        user_id = "test_user"
    
    data = []
    base_time = datetime.now()
    
    for i in range(count):
        query = fake.random_element(SAMPLE_QUERIES)
        casual_response = fake.random_element(SAMPLE_CASUAL_RESPONSES)
        formal_response = fake.random_element(SAMPLE_FORMAL_RESPONSES)
        
        data.append({
            "id": str(uuid4()),
            "user_id": user_id,
            "query": query,
            "casual_response": casual_response,
            "formal_response": formal_response,
            "created_at": (base_time - timedelta(minutes=i*10)).isoformat()
        })
    
    return data

def generate_sample_history_data(user_id: str = "test_user", count: int = 5) -> list:
    """Generate sample history data sorted by creation time (newest first)."""
    data = generate_sample_prompt_data(user_id, count)
    # Sort by created_at descending (newest first)
    return sorted(data, key=lambda x: x["created_at"], reverse=True)

def generate_multiple_users_data(user_count: int = 3, prompts_per_user: int = 3) -> dict:
    """Generate sample data for multiple users."""
    users_data = {}
    user_ids = generate_sample_user_ids(user_count)
    
    for user_id in user_ids:
        users_data[user_id] = generate_sample_history_data(user_id, prompts_per_user)
    
    return users_data

# Sample request payloads
SAMPLE_GENERATE_REQUESTS = [
    {
        "query": "What is artificial intelligence?",
        "user_id": "test_user_1"
    },
    {
        "query": "Explain machine learning algorithms",
        "user_id": "test_user_2"
    },
    {
        "query": "How does blockchain ensure security?",
        "user_id": "test_user_1"
    }
]

# Invalid request payloads for testing validation
INVALID_GENERATE_REQUESTS = [
    {},  # Empty request
    {"query": "test"},  # Missing user_id
    {"user_id": "test"},  # Missing query
    {"query": "", "user_id": ""},  # Empty values
    {"query": None, "user_id": "test"},  # None query
    {"query": "test", "user_id": None},  # None user_id
]

# Sample responses from AI generation
SAMPLE_AI_RESPONSES = [
    {
        "casual_response": "AI is basically computers that can think and learn like humans! It's pretty cool stuff that's everywhere these days.",
        "formal_response": "Artificial Intelligence represents the development of computer systems capable of performing tasks that typically require human intelligence."
    },
    {
        "casual_response": "Machine learning is like teaching your computer to recognize patterns and make smart guesses based on data!",
        "formal_response": "Machine Learning is a computational approach that enables systems to improve performance through experience and data analysis."
    }
]

# Database connection test data
TEST_DB_CONFIG = {
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "test_db"
}

# Edge case test data
EDGE_CASE_QUERIES = [
    "",  # Empty query
    " ",  # Whitespace only
    "a" * 10000,  # Very long query
    "What is AI? 🤖 How does it work & why is it important?",  # Special characters
    "SELECT * FROM users;",  # SQL injection attempt
    "<script>alert('test')</script>",  # XSS attempt
    "What is\nAI with\ttabs and\nnewlines?",  # Whitespace characters
]

# Performance test data
PERFORMANCE_TEST_QUERIES = [
    f"Query number {i} about artificial intelligence and machine learning" 
    for i in range(1, 101)
]

# API response templates
API_SUCCESS_RESPONSE_TEMPLATE = {
    "id": None,  # Will be filled with UUID
    "user_id": None,  # Will be filled
    "query": None,  # Will be filled
    "casual_response": None,  # Will be filled
    "formal_response": None,  # Will be filled
    "created_at": None  # Will be filled
}

API_ERROR_RESPONSE_TEMPLATE = {
    "detail": None  # Will be filled with error message
}

# Mock database responses
MOCK_DB_RESPONSES = {
    "insert_success": True,
    "insert_error": Exception("Database insertion failed"),
    "query_success": generate_sample_history_data(),
    "query_error": Exception("Database query failed"),
    "empty_result": []
}

# Load testing scenarios
LOAD_TEST_SCENARIOS = [
    {
        "name": "light_load",
        "concurrent_users": 5,
        "requests_per_user": 10,
        "delay_between_requests": 1
    },
    {
        "name": "medium_load", 
        "concurrent_users": 20,
        "requests_per_user": 25,
        "delay_between_requests": 0.5
    },
    {
        "name": "heavy_load",
        "concurrent_users": 50,
        "requests_per_user": 50,
        "delay_between_requests": 0.1
    }
]

# Authentication test data
AUTH_TEST_DATA = {
    "valid_user_ids": [
        "user_123",
        "test_user_456",
        "admin_789"
    ],
    "invalid_user_ids": [
        "",
        None,
        "user with spaces",
        "user@domain.com",
        "very_long_user_id_" + "x" * 100
    ]
}

# Pagination test data
PAGINATION_TEST_CASES = [
    {"limit": 5, "offset": 0, "expected_count": 5},
    {"limit": 10, "offset": 5, "expected_count": 5},
    {"limit": 1, "offset": 0, "expected_count": 1},
    {"limit": 100, "offset": 0, "expected_count": 10},  # Max available
    {"limit": 5, "offset": 100, "expected_count": 0},  # Beyond available data
]

# Content validation patterns
CONTENT_VALIDATION_PATTERNS = {
    "casual_indicators": [
        "like", "basically", "pretty", "super", "awesome", 
        "cool", "!", "you", "your", "we", "us"
    ],
    "formal_indicators": [
        "refers to", "encompasses", "represents", "consists of",
        "characterized by", "defined as", "involves", "comprises"
    ],
    "technical_terms": [
        "algorithm", "system", "process", "method", "approach",
        "technology", "mechanism", "framework", "architecture"
    ]
}

def create_test_prompt_object(user_id: str = "test_user", query: str = "Test query"):
    """Create a test prompt object matching database schema."""
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "query": query,
        "casual_response": fake.random_element(SAMPLE_CASUAL_RESPONSES),
        "formal_response": fake.random_element(SAMPLE_FORMAL_RESPONSES),
        "created_at": datetime.now()
    }

def create_mock_api_response(user_id: str, query: str):
    """Create a mock API response for testing."""
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "query": query,
        "casual_response": fake.random_element(SAMPLE_CASUAL_RESPONSES),
        "formal_response": fake.random_element(SAMPLE_FORMAL_RESPONSES),
        "created_at": datetime.now().isoformat()
    }

def get_sample_data_by_scenario(scenario: str):
    """Get sample data based on test scenario."""
    scenarios = {
        "success": SAMPLE_GENERATE_REQUESTS[0],
        "empty_query": {"query": "", "user_id": "test_user"},
        "long_query": {"query": "a" * 1000, "user_id": "test_user"},
        "special_chars": {"query": "What is AI? 🤖", "user_id": "test_user"},
        "multiple_users": generate_multiple_users_data()
    }
    return scenarios.get(scenario, SAMPLE_GENERATE_REQUESTS[0])