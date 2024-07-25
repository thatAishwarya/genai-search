import streamlit as st
import requests
import logging

# Define the FastAPI endpoint URLs
QUERY_ENDPOINT = "http://127.0.0.1:8000/query"
PROCESSDOCS_ENDPOINT = "http://127.0.0.1:8000/processdocs"

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Streamlit App
st.title("Finance Compliance Chat Bot")

# Create a top right column for the "Update Documents" button
top_right_column = st.columns([3, 1])[1]
with top_right_column:
    if st.button("Update Documents"):
        try:
            response = requests.post(PROCESSDOCS_ENDPOINT)
            if response.status_code == 200:
                st.success("Documents processed and embeddings updated.")
                logger.info("Documents processed and embeddings updated.")
            else:
                st.error(f"Failed to process documents: {response.text}")
                logger.error(f"Failed to process documents: {response.text}")
        except requests.RequestException as e:
            st.error(f"Error: {e}")
            logger.error(f"Error processing documents: {e}")

# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Function to add a message to the conversation history
def add_message(user_message, bot_message=None):
    if user_message:
        st.session_state.conversation.append({
            'type': 'user_query',
            'message': user_message
        })
        logger.debug(f"User message added: {user_message}")
    if bot_message:
        st.session_state.conversation.append({
            'type': 'bot',
            'message': bot_message
        })
        logger.debug(f"Bot message added: {bot_message}")

# Custom CSS to style the chat interface
st.markdown("""
    <style>
    .chat-container {
        background-color: #f0f0f0; /* Light grey background for the entire section */
        border-radius: 10px;
        padding: 10px;
        height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .user-query {
        background-color: #fff3cd; /* Pastel yellow */
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: #856404;
    }
    .bot-message {
        background-color: #cce5ff; /* Blue */
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        color: #004085;
    }
    </style>
    """, unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)

# Display the conversation history
for i, message in enumerate(st.session_state.conversation):
    if message['type'] == 'user_query':
        st.markdown(f"<div class='user-query'>{message['message']}</div>", unsafe_allow_html=True)
        if i+1 < len(st.session_state.conversation) and st.session_state.conversation[i+1]['type'] == 'bot':
            bot_message = st.session_state.conversation[i+1]['message']
            st.markdown(f"<div class='bot-message'>{bot_message}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Text input for user query at the bottom
user_query = st.text_input("Enter your query here:", key="user_input")

if st.button("Submit"):
    if user_query:
        add_message(user_query)  # Add user message to history
        
        try:
            # Send the query to the FastAPI backend
            response = requests.post(QUERY_ENDPOINT, json={"query": user_query})
            response_data = response.json()
            logger.info(f"Query sent: {user_query}")
            logger.debug(f"Response received: {response_data}")

            # Extract answer, referees, and suggestions
            answer = response_data.get("answer", "No answer found.")
            referees = response_data.get("referees", [])
            suggestions = response_data.get("suggestions", [])

            # Format bot response
            bot_message = f"**Answer:** {answer}\n\n"
            if referees:
                bot_message += f"**Referees:** {', '.join(referees)}\n\n"
            else:
                bot_message += "No referees found.\n\n"

            if suggestions:
                bot_message += f"**Suggested Queries:** {', '.join(suggestions)}"
            else:
                bot_message += "No suggestions available."
                
            add_message(None, bot_message)  # Add bot message to history

            # Force a re-render to display the updated conversation history
            st.experimental_rerun()

        except requests.RequestException as e:
            st.error(f"Error: {e}")
            logger.error(f"Error sending query: {e}")
    else:
        st.warning("Please enter a query.")
        logger.warning("No query entered.")
