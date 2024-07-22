import os
import logging
from typing import List, Callable
import pdfplumber
from langchain.schema import Document
from langchain.retrievers import BM25Retriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, directory_path: str, model_name: str = 'all-MiniLM-L6-v2'):
        self.directory_path = directory_path
        self.model_name = model_name

        # Initialize embeddings
        self.embeddings_model = SentenceTransformer(model_name)
        self.vectorstore = None
        self.bm25_retriever = None

    def load_documents(self) -> List[Document]:
        """Load PDF documents from the directory and return a list of Document objects."""
        documents = []
        for file_name in os.listdir(self.directory_path):
            file_path = os.path.join(self.directory_path, file_name)
            if file_path.lower().endswith('.pdf'):
                try:
                    with pdfplumber.open(file_path) as pdf:
                        text = ''.join(page.extract_text() or '' for page in pdf.pages)
                        if text.strip():  # Ensure text is not empty
                            documents.append(Document(page_content=text, metadata={"source": file_name}))
                        else:
                            logger.warning(f"Document {file_name} is empty after extraction.")
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
        if not documents:
            logger.warning("No documents loaded.")
        return documents

    def _embedding_function(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of texts using the SentenceTransformer model."""
        return self.embeddings_model.encode(texts, show_progress_bar=True).tolist()

    def initialize_vectorstore(self):
        """Initialize the vector store and BM25 retriever."""
        docs = self.load_documents()
        if not docs:
            raise ValueError("No documents found to initialize the vector store.")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        if not splits:
            raise ValueError("No document splits generated.")

        texts = [split.page_content for split in splits]
        ids = [str(i) for i in range(len(texts))]  # Generating unique IDs for each text split

        if not texts or not ids:
            raise ValueError("No texts or IDs generated for Chroma.")

        try:
            # Initialize Chroma with an embedding function
            self.vectorstore = Chroma(embedding_function=self._embedding_function)
            self.vectorstore.add_texts(texts=texts, ids=ids)
            
            self.bm25_retriever = BM25Retriever(docs=splits)
            logger.info("Vector store initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def add_documents_to_chroma(self, documents: List[Document]):
        """Add new documents to the existing vector store."""
        if not self.vectorstore:
            raise RuntimeError("Vector store is not initialized. Please call initialize_vectorstore first.")
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        if not splits:
            raise ValueError("No document splits generated.")

        texts = [split.page_content for split in splits]
        ids = [str(i) for i in range(len(texts))]  # Generating unique IDs for each text split

        if not texts or not ids:
            raise ValueError("No texts or IDs generated for Chroma.")

        try:
            self.vectorstore.add_texts(texts=texts, ids=ids)
            logger.info("Documents added to Chroma successfully.")
        except Exception as e:
            logger.error(f"Failed to add documents to Chroma: {e}")
            raise

    def search_query(self, query: str) -> List[str]:
        """Search for the query using BM25 retriever."""
        if not self.bm25_retriever:
            raise RuntimeError("BM25 retriever is not initialized. Please call initialize_vectorstore first.")
        
        return self.bm25_retriever.retrieve(query)

    def summarize_documents(self, documents: List[str]) -> List[str]:
        """Generate summaries for the provided documents."""
        return [self.generate_summary(doc) for doc in documents]

    def generate_summary(self, document: str) -> str:
        """Generate a summary of a document."""
        # Implement a simple summary generation or use an external service
        return "Summary of document"

    def suggest_queries(self, summary: str) -> List[str]:
        """Generate suggested queries based on the document summary."""
        # Placeholder logic: Implement a more sophisticated method based on your needs.
        return ["Suggested query based on the summary"]

    def update_index(self):
        """Update the index with documents from the directory."""
        documents = self.load_documents()
        if documents:
            self.add_documents_to_chroma(documents)
            self.bm25_retriever = BM25Retriever(docs=documents)
        else:
            logger.warning("No documents found for updating the index.")
