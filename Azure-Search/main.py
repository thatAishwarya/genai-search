from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from typing import List
from text_extraction import extract_text_from_file, process_documents
from embeddings import generate_embeddings
from search_utils import create_search_index, upload_documents
from openai_utils import search_and_generate_answer

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/upload")
async def upload_documents_endpoint(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload documents, extract text, generate embeddings, and upload to Azure Search.
    """
    documents = []
    file_names = []

    for uploaded_file in files:
        file_path = os.path.join("uploads", uploaded_file.filename)
        with open(file_path, "wb") as f:
            content = await uploaded_file.read()
            f.write(content)
        file_names.append(uploaded_file.filename)
        content_text = extract_text_from_file(file_path)
        documents.append(content_text)

    embeddings = [generate_embeddings(doc) for doc in documents]

    create_search_index()
    upload_documents(documents, embeddings)

    return {"message": "Documents uploaded and indexed successfully!"}

@app.post("/process")
async def process_documents_endpoint():
    """
    Endpoint to process all documents from the ../Data/TCA directory, extract text, generate embeddings, and upload to Azure Search.
    """
    documents, file_names = process_documents()

    embeddings = [generate_embeddings(doc) for doc in documents]

    create_search_index()
    upload_documents(documents, embeddings)

    return {"message": "Documents processed, indexed successfully!"}

@app.post("/query")
async def query_documents_endpoint(query: Query):
    """
    Endpoint to query the documents and generate a response using OpenAI.
    """
    if not query.query:
        raise HTTPException(status_code=400, detail="No query provided")

    answer, results = search_and_generate_answer(query.query)

    response = {
        "answer": answer,
        "references": [{"id": result['id'], "content": result['content'][:200]} for result in results]
    }

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
