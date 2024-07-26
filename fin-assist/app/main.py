import os
import logging
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import PyPDF2
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Configuration settings
SETTINGS = {
    "PDF_DIR": "data/TCA-Test",
    "PERSIST_DIRECTORIES": {
        "llama3.1": "data/llama3.1",
        "gpt-3.5-turbo": "data/gpt-3.5-turbo"
    },
    "LLM_MODELS": {
        # "llama3.1": {    #Commenting this option, uncomment for demo
        #     "llm": Ollama,
        #     "embedding": OllamaEmbeddings,
        #     "embedding_model": "mxbai-embed-large",
        #     "model_name": "llama3.1"
        # },
        "gpt-3.5-turbo": {
            "embedding": OpenAIEmbeddings,
            "embedding_model": "text-embedding-3-small",
            "model_name": "gpt-3.5-turbo"
        }
    },
    "DEFAULT_MODEL": "llama3.1",
    "LLM_BASE_URL": "http://localhost:11434",
    "PROMPT_TEMPLATE": """You are a knowledgeable chatbot, here to help with questions of the user. Your tone should be professional and informative.
        Context: {context}
        History: {history}
        User: {question}
        Chatbot:""",
    "LOGGING_LEVEL": logging.DEBUG,
    "OPENAI_API_KEY": ""
}

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

# Set up logging configuration
logging.basicConfig(level=SETTINGS["LOGGING_LEVEL"], format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
vectorstores = {}
qa_chains = {}

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
                            # Include metadata with the document name and page number
                            page_texts.append({
                                "filename": filename,
                                "page_num": page_num + 1,
                                "content": page_text
                            })
                            logger.debug(f"Extracted text from page {page_num + 1} of file {filename}")
            except Exception as e:
                logger.error(f"Error processing file {filepath}: {e}")
    return page_texts

def update_embeddings(model_key):
    logger.info(f"Updating embeddings for model {model_key}.")
    try:
        # Extract text from PDFs
        page_texts = extract_text_from_pdfs(SETTINGS["PDF_DIR"])
        
        # Create document objects from text pages
        documents = [
            Document(
                page_content=text["content"],
                metadata={"filename": text["filename"], "page_num": text["page_num"]}
            )
            for text in page_texts
        ]
        
        # Select embedding model and directory based on the selected model
        model_config = SETTINGS["LLM_MODELS"][model_key]
        
        if model_key == "llama3.1":
            embedding_function = OllamaEmbeddings(model="mxbai-embed-large")
        elif model_key == "gpt-3.5-turbo":
            embedding_function = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=SETTINGS["OPENAI_API_KEY"])
        else:
            raise ValueError(f"Unsupported model key: {model_key}")
        
        persist_directory = SETTINGS["PERSIST_DIRECTORIES"][model_key]
        
        # Create or update vector store
        vectorstore = Chroma.from_documents(
            documents=documents, 
            embedding=embedding_function,
            persist_directory=persist_directory
        )
        logger.info(f"Vector store for {model_key} created or updated and persisted.")
        return vectorstore

    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise


def load_vectorstores():
    logger.info("Loading vector stores.")
    try:
        for model_key in SETTINGS["LLM_MODELS"].keys():
            persist_directory = SETTINGS["PERSIST_DIRECTORIES"][model_key]
            if os.path.exists(persist_directory):
                logger.info(f"Loading vector store for model {model_key}.")
                # Create embedding object based on model_key
                model_config = SETTINGS["LLM_MODELS"][model_key]
                if model_key == "gpt-3.5-turbo":
                    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=SETTINGS["OPENAI_API_KEY"])
                else:
                    embedding_function = OllamaEmbeddings(model="mxbai-embed-large")
                vectorstores[model_key] = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
            else:
                logger.info(f"No existing vector store found for model {model_key}.")
        logger.info("All vector stores loaded.")
    except Exception as e:
        logger.error(f"Error loading vector stores: {e}")
        raise

def create_qa_chain(model_key):
    global qa_chains
    if model_key in qa_chains:
        logger.info(f"QA chain for {model_key} already created.")
        return qa_chains[model_key]

    logger.info(f"Creating QA chain for model {model_key}.")
    try:
        # Get the corresponding vector store
        vectorstore = vectorstores.get(model_key)
        if not vectorstore:
            logger.error(f"Vector store for {model_key} not found.")
            raise ValueError(f"Vector store for {model_key} not found.")
        
        model_config = SETTINGS["LLM_MODELS"][model_key]
        if model_key == "gpt-3.5-turbo":
            llm = ChatOpenAI(model=model_config["model_name"], openai_api_key=SETTINGS["OPENAI_API_KEY"])
        else:
            llm = model_config["llm"](base_url=SETTINGS["LLM_BASE_URL"], model=model_config["model_name"], verbose=True)
        
        retriever = vectorstore.as_retriever()

        prompt = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=SETTINGS["PROMPT_TEMPLATE"],
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
        qa_chains[model_key] = qa_chain
        logger.info(f"QA chain for {model_key} created.")
        return qa_chain

    except Exception as e:
        logger.error(f"Error creating QA chain: {e}")
        raise

@app.on_event("startup")
async def application_start():
    logger.info("Application startup.")
    try:
        # Load vector stores if they exist, otherwise create them
        for model_key in SETTINGS["LLM_MODELS"].keys():
            persist_directory = SETTINGS["PERSIST_DIRECTORIES"][model_key]
            if not os.path.exists(persist_directory):
                # Create vector store if it does not exist
                vectorstores[model_key] = update_embeddings(model_key)
            else:
                # Load existing vector store
                load_vectorstores()
        
        # Create QA chains for each model using the vector stores
        for model_key in SETTINGS["LLM_MODELS"].keys():
            if model_key not in vectorstores:
                vectorstores[model_key] = update_embeddings(model_key)
            create_qa_chain(model_key)
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise HTTPException(status_code=500, detail="Application startup failed")

@app.post("/processdocs")
async def process_docs():
    logger.info("Processing documents.")
    try:
        # Force update embeddings and reinitialize vector stores
        for model_key in SETTINGS["LLM_MODELS"].keys():
            vectorstores[model_key] = update_embeddings(model_key)
        
        # Recreate QA chains for each model after updating embeddings
        for model_key in SETTINGS["LLM_MODELS"].keys():
            create_qa_chain(model_key)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class QueryData(BaseModel):
    query: str
    model: str

@app.post("/query")
async def query(query_data: QueryData):
    query_text = query_data.query
    model_key = query_data.model
    logger.info(f"Received query: {query_text} for model: {model_key}")
    try:
        # Create QA chain if it does not exist for the requested model
        if model_key not in qa_chains:
            create_qa_chain(model_key)
        
        qa_chain = qa_chains[model_key]
        result = qa_chain({"query": query_text})
        
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
