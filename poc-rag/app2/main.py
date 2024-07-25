import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import PyPDF2
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document

app = FastAPI()

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directory containing PDF files
PDF_DIR = "../data/TCA"
PERSIST_DIRECTORY = 'data'

def extract_text_from_pdfs(pdf_dir):
    logger.info(f"Extracting text from PDFs in directory: {pdf_dir}")
    page_texts = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            logger.debug(f"Processing file: {filepath}")
            try:
                with open(filepath, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append((filename, page_num + 1, page_text))
                            logger.debug(f"Extracted text from page {page_num + 1} of file {filename}")
            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}")
    return page_texts

def update_embeddings():
    logger.info("Updating embeddings.")
    try:
        # Extract text from PDFs
        page_texts = extract_text_from_pdfs(PDF_DIR)
        
        # Create document objects from text pages
        documents = [Document(page_content=text[2]) for text in page_texts]
        
        # Initialize OllamaEmbeddings for embedding generation
        embedding_function = OllamaEmbeddings(model="mxbai-embed-large")

        # Create or update vector store
        vectorstore = Chroma.from_documents(
            documents=documents, 
            embedding=embedding_function,
            persist_directory=PERSIST_DIRECTORY
        )
        logger.info("Vector store created or updated and persisted.")
        return vectorstore

    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise

def initialize_chroma_and_qa_chain():
    logger.info("Initializing Chroma and QA chain.")
    try:
        # Always update embeddings
        vectorstore = update_embeddings()
        
        llm = Ollama(base_url="http://localhost:11434", model="llama3.1", verbose=True)
        retriever = vectorstore.as_retriever()

        template = """You are a knowledgeable chatbot, here to help with questions of the user. Your tone should be professional and informative.
            Context: {context}
            History: {history}
            User: {question}
            Chatbot:"""
        
        prompt = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=template,
        )
        
        memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            input_key="question"
        )
        logger.info("Initialize RetrievalQA chain")
        
        # Initialize RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            verbose=True,
            chain_type_kwargs={
                "verbose": True,
                "prompt": prompt,
                "memory": memory,
            }
        )
        logger.info("QA chain initialized.")
        return qa_chain

    except Exception as e:
        logger.error(f"Error initializing Chroma and QA chain: {e}")
        raise

@app.post("/processdocs")
async def process_docs():
    logger.info("Processing documents.")
    try:
        # Update embeddings and reinitialize QA chain
        global qa_chain
        qa_chain = initialize_chroma_and_qa_chain()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class QueryData(BaseModel):
    query: str

@app.post("/query")
async def query(query_data: QueryData):
    query_text = query_data.query
    logger.info(f"Received query: {query_text}")
    try:
        result = qa_chain({"query": query_text})
        logger.debug(f"Query result: {result}")
        return {
            "answer": result.get("result"),
            "referees": result.get("referees", []),
            "suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
