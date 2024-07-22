from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from search_engine import SearchEngine
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

class QueryModel(BaseModel):
    query: str

class SyncResponse(BaseModel):
    status: str

# Initialize the search engine with your API key and document directory
search_engine = SearchEngine(directory_path='../data/TCA-Test')

@app.post("/query")
def query(query_model: QueryModel):
    response = search_engine.search_query(query_model.query)
    summaries = search_engine.summarize_documents(response)
    suggested_queries = search_engine.suggest_queries(summaries[0] if summaries else "")
    return JSONResponse(content={
        "summary": summaries,
        "references": response,
        "suggested_queries": suggested_queries
    })

@app.post("/syncdocs")
def sync_docs():
    logging.info("syncdocs endpoint was called")
    search_engine.initialize_vectorstore()
    search_engine.update_index(search_engine.documents)
    return JSONResponse(content={"status": "Documents synced successfully."})
