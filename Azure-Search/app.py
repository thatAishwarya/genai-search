import streamlit as st
from pydantic import BaseModel
import requests

# URL of the FastAPI endpoints
API_BASE_URL = "http://localhost:8000"

class Query(BaseModel):
    query: str

def query_documents(query_text):
    """
    Query the FastAPI endpoint to get the summary and references.
    """
    response = requests.post(f"{API_BASE_URL}/query", json={"query": query_text})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error querying the documents.")
        return None

def main():
    st.title("Document Query Interface")

    st.write("Enter your query below:")

    user_query = st.text_input("Query", "")

    if st.button("Submit"):
        if user_query:
            with st.spinner("Processing..."):
                result = query_documents(user_query)
                if result:
                    st.subheader("Summary:")
                    st.write(result.get("answer", "No answer found."))
                    
                    st.subheader("References:")
                    references = result.get("references", [])
                    if references:
                        for ref in references:
                            st.write(f"ID: {ref['id']}")
                            st.write(f"Content: {ref['content']}")
                            st.write("---")
                    else:
                        st.write("No references found.")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
