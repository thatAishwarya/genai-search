
# FinAssist

FinAssist is a chatbot application designed to assist users with queries related to financial documents. The chatbot leverages natural language processing and embeddings to provide relevant responses based on the content of the uploaded documents.

## Features

- **Chat Interface**: A web-based chat interface for interacting with the chatbot.
- **Document Synchronization**: Syncs and processes documents to update the chatbot's knowledge base.
- **Natural Language Understanding**: Uses embeddings and retrieval mechanisms to answer user queries accurately.

## Project Structure

- `main.py`: FastAPI backend for document processing and chatbot queries.
- `static/`: Contains static files (HTML, CSS, JavaScript) for the front-end interface.
- `data/`: Directory for storing PDF documents and vector store data.
- `chatbot.js`: JavaScript file for handling chat interactions and API calls.
- `static/css/style.css`: CSS file for styling the chat interface.

## Prerequisites

- Python 3.8+
- Pip (Python package installer)
- Node.js (for any front-end dependencies)
- `Ollama` CLI (for running local models)

## Installation

### Backend Setup

1. **Clone the Repository**

Create a folder "genai-search" on your machine
   ```bash
   git clone https://github.com/thatAishwarya/genai-search
   cd genai-search/fin-assist
   ```

2. **Create and Activate a Virtual Environment (Can be skipped)** 

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Python Dependencies**

   Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install and Run `Ollama`**

   - **Install `Ollama CLI`**:

     - **For macOS**:

       ```bash
       brew install ollama
       ```

     - **For Linux**:

       Download the Linux binary from the [Ollama GitHub Releases](https://github.com/ollama/ollama/releases) and follow the installation instructions.

     - **For Windows**:

       Download the Windows installer from the [Ollama GitHub Releases](https://github.com/ollama/ollama/releases) and follow the installation instructions.

   - **Run `Ollama` Server**:

     ```bash
     ollama run llama3.1
     ```

     Ensure the server is running and accessible on the default port (11434) or the port you specify.

5. **Start the FastAPI Server**
   cd app
   ```bash
   uvicorn app:app --reload
   ```

### Front-End Setup

1. **Ensure Static Files Are Correct**

   - Place your `index.html`, CSS, and JavaScript files in the `static/` directory.

2. **Install Front-End Dependencies**

   If you have additional JavaScript libraries or frameworks, install them as needed. For example:

   ```bash
   npm install
   ```

3. **Access the Application**

   Open your web browser and navigate to `http://localhost:8000` to view and interact with the chat interface.

## Usage

### Sync Documents

- Click the "Sync Documents" button to process and update the chatbot's knowledge base with new or updated documents. This will extract text from the PDFs located in the `data/TCA` directory and update the vector store.

### Query the Chatbot

- Enter your query in the input field at the bottom of the chat interface and click "Submit" to receive a response from the chatbot.

## Troubleshooting

### Common Issues

- **Embedding Function Error**: Ensure that the `OllamaEmbeddings` is correctly initialized and passed to the `Chroma` vector store. Verify the model name and refer to the [Chroma documentation](https://docs.trychroma.com/guides/embeddings) for guidance.

- **Missing Dependencies**: Check your `requirements.txt` file to ensure all necessary libraries are installed. Run `pip install -r requirements.txt` to install missing dependencies.

- **Server Not Starting**: Ensure that the FastAPI server is running and that you are navigating to the correct URL (`http://localhost:8000`).

## Development

### Running Tests

If tests are available, you can run them using:

```bash
pytest
```


## Acknowledgments

- **LangChain**: For providing powerful NLP capabilities.
- **Chroma**: For the vector store functionalities.

---

Feel free to adjust or expand this `README.md` based on specific details or additional requirements of your project.