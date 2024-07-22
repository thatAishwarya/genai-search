import streamlit as st
from search_engine import SearchEngine

def fetch_response(endpoint: str, params: dict = None):
    """
    Fetch response from the local FastAPI endpoint with optional parameters.
    
    :param endpoint: The endpoint to call.
    :param params: Optional parameters for the request.
    :return: The response from the API.
    """
    import requests
    if params is None:
        response = requests.post(f"http://localhost:8000/{endpoint}")
    else:
        response = requests.post(f"http://localhost:8000/{endpoint}", json=params)
    return response.json()

def main():
    st.title("Chatbot Interface")

    # Initialize the SearchEngine
    search_engine = SearchEngine(directory_path='../data/TCA', openai_api_key='sk-proj-75d1wXZdetEgtp5jtMgAT3BlbkFJGIt3oWLrvBKjlLI6A7Cu')

    # Input Box for User Message
    st.subheader("Ask a Question:")
    user_message = st.text_input("You:", "")

    if st.button("Send"):
        if user_message:
            # Fetch results from SearchEngine
            results = search_engine.search_query(user_message)
            summary = search_engine.summarize_documents(results)
            suggestions = search_engine.suggest_queries(" ".join(summary))

            # Display Summary
            st.subheader("Summary:")
            for s in summary:
                st.text(s)

            # Display Suggested Queries
            st.subheader("Suggested Queries:")
            for query in suggestions:
                st.text(query)

    if st.button("Sync Docs"):
        sync_response = fetch_response("syncdocs")
        st.text(sync_response.get("status", "Failed to sync documents."))

if __name__ == "__main__":
    main()
