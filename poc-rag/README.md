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
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
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
    uvicorn main:app --reload
    ```

   This will start the FastAPI server at `http://127.0.0.1:8000`.

### Running the Streamlit Frontend

1. **Start the Streamlit app:**

    ```bash
    streamlit run ui.py
    ```

   This will open the Streamlit app in your web browser, where you can interact with the document processing and querying system.

### Syncing Documents

To sync the documents with the backend, use the "Sync Docs" button in the Streamlit interface. This will reprocess and index the documents located in the specified folder.

## Project Structure

- `document_processing.py`: Contains the `DocumentProcessor` class for loading and cleaning PDFs.
- `embedding_indexing.py`: Defines the `EmbeddingIndexer` class for creating and querying the document index.
- `summarizer_integration.py`: Implements the `SummarizerModel` class for summarizing text.
- `service_context.py`: Contains the `ServiceContext` class to manage interactions between components.
- `main.py`: The FastAPI application script.
- `ui.py`: The Streamlit frontend application script.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request with your changes. Ensure that your contributions adhere to the project's coding standards and guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for building the web API.
- Streamlit for creating interactive web applications.
- Sentence Transformers and Transformers for advanced text processing.
- FAISS for efficient similarity search.
