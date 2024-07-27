import os
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
    try:
        # Create QA chain if it does not exist for the requested model
        if model_key not in qa_chains:
            logger.info("Creating chain")
            qa_chains = search.create_qa_chain(model_key, vectorstores)
        
        logger.info("Initailising qa_chain")
        qa_chain = qa_chains[model_key]
        logger.info("Getting Result")
        result = qa_chain({"query": query_text})
        
        logger.info("Refining Result")
        # Extract references (document name and page number) from the results
        referees = []
        if "result" in result and "metadata" in result:
            referees = [
                {
                    "filename": doc_metadata["filename"],
                    "page_num": doc_metadata["page_num"]
                }
                for doc_metadata in result["metadata"]
            ]
        
        logger.debug(f"Query result: {result}")
        return {
            "answer": result.get("result"),
            "referees": referees,
            "suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return RedirectResponse(url="/static/chatbot.html")
