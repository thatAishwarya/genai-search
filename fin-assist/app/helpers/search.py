import os
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document


from helpers import document_reader 
from app_config import SETTINGS
from logging_config import setup_logging

# Initialize logging
logger = setup_logging()

def update_embeddings(model_key):
    logger.info(f"Updating embeddings for model {model_key}.")
    try:
        # Extract text from PDFs
        page_texts = document_reader.extract_text_from_pdfs(SETTINGS["PDF_DIR"])
        
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
            embedding_function = OllamaEmbeddings(model=model_config["embedding_model"])
        elif model_key == "gpt-3.5-turbo":
            embedding_function = OpenAIEmbeddings(model=model_config["embedding_model"], openai_api_key=SETTINGS["OPENAI_API_KEY"])
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

def load_vectorstores(vectorstores):
    logger.info("Loading vector stores.")
    try:
        for model_key in SETTINGS["LLM_MODELS"].keys():
            persist_directory = SETTINGS["PERSIST_DIRECTORIES"][model_key]
            if os.path.exists(persist_directory):
                logger.info(f"Loading vector store for model {model_key}.")
                # Create embedding object based on model_key
                model_config = SETTINGS["LLM_MODELS"][model_key]
                if model_key == "gpt-3.5-turbo":
                    embedding_function = OpenAIEmbeddings(model=model_config["embedding_model"], openai_api_key=SETTINGS["OPENAI_API_KEY"])
                else:
                    embedding_function = OllamaEmbeddings(model=model_config["embedding_model"])
                vectorstores[model_key] = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)
            else:
                logger.info(f"No existing vector store found for model {model_key}.")
        logger.info("All vector stores loaded.")
        return vectorstores
    except Exception as e:
        logger.error(f"Error loading vector stores: {e}")
        raise

def create_qa_chain(model_key, vectorstores, qa_chains):
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
            llm = Ollama(base_url=SETTINGS["LLM_BASE_URL"], model=model_config["model_name"], verbose=True)
        
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
        return qa_chains

    except Exception as e:
        logger.error(f"Error creating QA chain: {e}")
        raise