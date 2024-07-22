from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from document_processing import DocumentProcessor
from embedding_indexing import EmbeddingIndexer
from summarizer_integration import SummarizerModel  # Update import to new summarizer model
from service_context import ServiceContext

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize components
try:
    doc_processor = DocumentProcessor(folder_path='../data/TCA-Test')
    documents = doc_processor.load_pdfs()
    embedding_indexer = EmbeddingIndexer()
    summarizer_model = SummarizerModel()  # Use SummarizerModel instead of LlamaModel
    service_context = ServiceContext(summarizer_model, embedding_indexer)  # Adjust initialization
    logger.info("Components initialized successfully.")
except Exception as e:
    logger.error(f"Error during initialization: {e}")
    raise HTTPException(status_code=500, detail="Error during initialization")

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    try:
        summary, references, suggested_queries = service_context.handle_query(request.query)
        response = {
            "summary": summary,
            "references": references,
            "suggested_queries": suggested_queries
        }
        logger.info("Query processed successfully.")
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")

@app.post("/syncdocs")
async def sync_docs():
    try:
        global documents
        logger.info("Syncing documents...")
        doc_processor = DocumentProcessor(folder_path='../data/TCA-Test')
        documents = doc_processor.load_pdfs()
        embedding_indexer.create_index(documents)
        logger.info("Documents synced and index updated successfully.")
        return {"status": "Documents synced and index updated successfully."}
    except Exception as e:
        logger.error(f"Error syncing documents: {e}")
        raise HTTPException(status_code=500, detail="Error syncing documents")

