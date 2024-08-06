import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app_config import SETTINGS
from logging_config import setup_logging
from helpers import search

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to restrict access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data/TCA", StaticFiles(directory="data/TCA"), name="data")

# Initialize logging
logger = setup_logging()

# Global variables
vectorstores = {}
qa_chains = {}

@app.on_event("startup")
async def application_start():
    global vectorstores, qa_chains
    logger.info("Application startup.")
    try:
        # Load vector stores if they exist, otherwise create them
        for model_key in SETTINGS["LLM_MODELS"].keys():
            persist_directory = SETTINGS["PERSIST_DIRECTORIES"][model_key]
            if not os.path.exists(persist_directory):
                # Create vector store if it does not exist
                vectorstores[model_key] = search.update_embeddings(model_key)
            else:
                # Load existing vector store
                vectorstores = search.load_vectorstores(vectorstores)
        
        # Create QA chains for each model using the vector stores
        for model_key in SETTINGS["LLM_MODELS"].keys():
            if model_key not in qa_chains:
                qa_chains = search.create_qa_chain(model_key, vectorstores, qa_chains)
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise HTTPException(status_code=500, detail="Application startup failed")

@app.post("/processdocs")
async def process_docs():
    global vectorstores, qa_chains
    logger.info("Processing documents.")
    try:
        # Force update embeddings and reinitialize vector stores
        for model_key in SETTINGS["LLM_MODELS"].keys():
            vectorstores[model_key] = search.update_embeddings(model_key)
        
        # Recreate QA chains for each model after updating embeddings
        for model_key in SETTINGS["LLM_MODELS"].keys():
            qa_chains = search.create_qa_chain(model_key, vectorstores, qa_chains)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class QueryData(BaseModel):
    query: str
    model: str

@app.post("/query")
async def query(query_data: QueryData):
    global vectorstores, qa_chains
    query_text = query_data.query
    model_key = query_data.model
    logger.info(f"Received query: {query_text} for model: {model_key}")
    logger.info(f"QA Chain: {qa_chains} for vectorstores: {vectorstores}")
    start_time = time.time()
    try:
        # Create QA chain if it does not exist for the requested model
        if model_key not in qa_chains:
            logger.info("Creating chain")
            qa_chains = search.create_qa_chain(model_key, vectorstores)
        
        logger.info("Initailising qa_chain")
        qa_chain = qa_chains[model_key]
        logger.info("Getting Result")
        result = qa_chain({"query": query_text})
    
        # Extract references (document name and page number) from the results
        references = []
        if "source_documents" in result:
            source_docs = result["source_documents"]
            if isinstance(source_docs, list):
                references = [
                    {
                        "filename": doc.metadata.get("filename", "Unknown"),
                        "page_num": doc.metadata.get("page_num", "Unknown")
                    }
                    for doc in source_docs if hasattr(doc, "metadata") and isinstance(doc.metadata, dict)
                ]
        
        logger.debug(f"Query result: {result}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        return {
            "answer": result.get("result", "No answer provided"),
            "references": references,
            "suggestions": result.get("suggestions", []),
            "time_taken": elapsed_time
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class CompareQueryData(BaseModel):
    query: str

@app.post("/compare")
async def compare(query_data: CompareQueryData):
    global vectorstores, qa_chains
    query_text = query_data.query
    logger.info(f"Received query for comparison: {query_text}")
    
    try:
        responses = {}
        for model_key in SETTINGS["LLM_MODELS"].keys():
            start_time = time.time()
            if model_key not in qa_chains:
                logger.info(f"Creating chain for model: {model_key}")
                qa_chains = search.create_qa_chain(model_key, vectorstores, qa_chains)
            
            logger.info(f"Processing query with model: {model_key}")
            qa_chain = qa_chains[model_key]
            result = qa_chain({"query": query_text})
             # Extract references (document name and page number) from the results
            references = []
            if "source_documents" in result:
                source_docs = result["source_documents"]
                if isinstance(source_docs, list):
                    references = [
                        {
                            "filename": doc.metadata.get("filename", "Unknown"),
                            "page_num": doc.metadata.get("page_num", "Unknown")
                        }
                        for doc in source_docs if hasattr(doc, "metadata") and isinstance(doc.metadata, dict)
                    ]
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            responses[model_key] = {
                "answer": result.get("result"),
                "references": references,
                "suggestions": result.get("suggestions", []),
                "time_taken": elapsed_time
            }
        
        return responses
    except Exception as e:
        logger.error(f"Error processing comparison query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return RedirectResponse(url="/static/chatbot.html")
