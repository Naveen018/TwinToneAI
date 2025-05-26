import streamlit as st
import requests
import os
import logging
import string
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def fetch_user_ids() -> list:
    """
    Fetch all distinct user_ids from the backend.
    
    Returns:
        list: List of user_id strings.
    """
    try:
        logger.info("Fetching user_ids from %s/users", API_BASE_URL)
        response = requests.get(f"{API_BASE_URL}/users", timeout=10)
        response.raise_for_status()
        user_ids = response.json().get("user_ids", [])
        logger.info("Retrieved %d user_ids", len(user_ids))
        return user_ids
    except requests.RequestException as e:
        logger.error("Failed to fetch user_ids: %s", str(e))
        st.error(f"Failed to fetch user_ids: {str(e)}")
        return []

def generate_response(user_id: str, query: str) -> dict:
    """
    Call the /generate endpoint to get casual and formal responses.
    
    Args:
        user_id (str): User identifier.
        query (str): User query.
    
    Returns:
        dict: API response containing casual and formal responses.
    """
    try:
        logger.info("Sending request to %s/generate for user_id: %s", API_BASE_URL, user_id)
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json={"user_id": user_id, "query": query},
            timeout=30
        )
        response.raise_for_status()
        logger.info("Received response for user_id: %s", user_id)
        return response.json()
    except requests.Timeout:
        logger.error("Request timed out after 30 seconds for user_id: %s", user_id)
        st.error("Request timed out. Please try again.")
        return None
    except requests.HTTPError as e:
        logger.error("HTTP error for user_id %s: %s", user_id, str(e))
        st.error(f"Server error: {str(e)}")
        return None
    except requests.RequestException as e:
        logger.error("Failed to generate responses for user_id: %s: %s", user_id, str(e))
        st.error(f"Failed to generate responses: {str(e)}")
        return None

def fetch_history(user_id: str) -> list:
    """
    Retrieve past interactions for a given user.
    
    Args:
        user_id (str): User identifier.
    
    Returns:
        list: List of user queries and responses.
    """
    try:
        logger.info("Fetching history for user_id: %s", user_id)
        response = requests.get(
            f"{API_BASE_URL}/history/{user_id}",
            params={"limit": 50, "offset": 0},
            timeout=10
        )
        response.raise_for_status()
        logger.info("Retrieved %d records for user_id: %s", len(response.json()), user_id)
        return response.json()
    except requests.RequestException as e:
        logger.error("Failed to fetch history for user_id %s: %s", user_id, str(e))
        st.error(f"Failed to fetch history: {str(e)}")
        return []

# Initialize session state
if "generated_response" not in st.session_state:
    st.session_state["generated_response"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "abc123"  # Default user_id
if "user_ids" not in st.session_state:
    st.session_state["user_ids"] = fetch_user_ids()  # Fetch user_ids once per session

# Streamlit UI
st.set_page_config(page_title="TwinToneAI", layout="wide")
st.title("TwinToneAI: Dual-Tone AI Responses")

# Sidebar for history
with st.sidebar:
    st.header("Interaction History")
    # Dynamic dropdown for user_id selection
    user_id_history = st.selectbox(
        "Select User ID",
        options=st.session_state["user_ids"] or ["No users available"],
        index=st.session_state["user_ids"].index(st.session_state["user_id"]) if st.session_state["user_id"] in st.session_state["user_ids"] else 0,
        key="user_id_history"
    )
    
    if user_id_history and user_id_history != "No users available":
        with st.spinner("Loading history..."):
            history = fetch_history(user_id_history)
            if history:
                for record in history:
                    with st.expander(f"Query: {record['query']} ({record['created_at']})"):
                        st.subheader("Casual Response")
                        st.write(record["casual_response"] or "No response")
                        st.subheader("Formal Response")
                        st.write(record["formal_response"] or "No response")
            else:
                st.info("No history found for this user.")
    else:
        st.warning("No user IDs available. Generate a response to create a new user.")

# Main content with form
st.header("Generate New Response")
with st.form(key="generate_form", clear_on_submit=False):
    user_id = st.text_input("User ID", value=st.session_state["user_id"], key="user_id_form")
    query = st.text_area("Query", placeholder="e.g., Explain blockchain", height=100, max_chars=1000)
    submit_button = st.form_submit_button("Generate Response")

    if submit_button:
        errors = []
        # Validate User ID
        if not user_id:
            errors.append("User ID cannot be empty.")
        
        # Validate Query
        if not query or query.isspace():
            errors.append("Query cannot be empty or just whitespace.")
        elif len(query) > 1000:
            errors.append("Query cannot exceed 1000 characters.")
        elif not all(c in string.printable for c in query):
            errors.append("Query contains invalid characters. Use printable characters only.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            with st.spinner("Generating responses..."):
                result = generate_response(user_id, query)
                if result:
                    st.session_state["generated_response"] = result
                    st.session_state["user_id"] = user_id  # Update persisted user_id

# Display generated response in two columns
if st.session_state["generated_response"]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Casual Response")
        st.write(st.session_state["generated_response"]["casual_response"])
    with col2:
        st.subheader("Formal Response")
        st.write(st.session_state["generated_response"]["formal_response"])

# Styling for readability
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 16px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
    }
    .stExpander {
        border: 1px solid #ddd;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)