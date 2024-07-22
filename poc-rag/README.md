# Document Processing and Query System

This project is a document processing and querying system that extracts text from PDFs, indexes it, and allows querying of the indexed data. It uses FastAPI for the backend, Streamlit for the frontend, and various machine learning models for text processing and summarization.

## Features

- Extracts and cleans text from PDF documents.
- Indexes documents using embeddings for efficient querying.
- Provides summarization and query handling through a FastAPI backend.
- Interactive frontend with Streamlit for user interaction.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/thatAishwarya/genai-search
    cd your-folder/poc-rag
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory with the following content:

    ```dotenv
    FASTAPI_URL=http://127.0.0.1:8000
    ```

## Usage

### Running the FastAPI Backend

1. **Start the FastAPI server:**

    ```bash
    cd app
    uvicorn main:app --reload
    ```

   This will start the FastAPI server at `http://127.0.0.1:8000`.

### Running the Streamlit Frontend

1. **Start the Streamlit app:**

    ```bash
    cd ui
    streamlit run chat.py
    ```

   This will open the Streamlit app in your web browser, where you can interact with the document processing and querying system.


## Project Structure

- `document_processing.py`: Contains the `DocumentProcessor` class for loading and cleaning PDFs.
- `embedding_indexing.py`: Defines the `EmbeddingIndexer` class for creating and querying the document index.
- `summarizer_integration.py`: Implements the `SummarizerModel` class for summarizing text.
- `service_context.py`: Contains the `ServiceContext` class to manage interactions between components.
- `main.py`: The FastAPI application script.
- `ui.py`: The Streamlit frontend application script.

