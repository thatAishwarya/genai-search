import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FASTAPI_URL = "http://127.0.0.1:8000"

def fetch_response(endpoint, params=None):
    """
    Helper function to fetch response from FastAPI endpoint.
    
    :param endpoint: The endpoint to call.
    :param params: Optional parameters to send with the request.
    :return: The response from the API.
    """
    response = requests.post(f"{FASTAPI_URL}/{endpoint}", json=params)
    response.raise_for_status()  # Ensure we raise an exception for HTTP errors
    return response.json()

def main():
    st.title("AI Search")

    # Input Box for User Message
    st.subheader("Ask a Question:")
    user_message = st.text_input("You:", "")

    if st.button("Send"):
        if user_message:
            try:
                # Send message to FastAPI
                chat_response = fetch_response("query", {"query": user_message})
                summary = chat_response.get("summary", ["No summary available."])
                references = chat_response.get("references", [])
                suggested_queries = chat_response.get("suggested_queries", [])

                # Display Summary
                st.subheader("Summary:")
                for s in summary:
                    st.text(s)

                # Display References
                st.subheader("References:")
                for ref in references:
                    st.text(ref)

                # Display Suggested Queries
                st.subheader("Suggested Queries:")
                for query in suggested_queries:
                    st.text(query)
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

    if st.button("Sync Docs"):
        try:
            sync_response = fetch_response("syncdocs")
            st.text(sync_response.get("status", "Failed to sync documents."))
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
