import logging

# Configuration settings
SETTINGS = {
    "PDF_DIR": "data/TCA",
    "PERSIST_DIRECTORIES": {
        "llama3.1": "data/llama3.1",
        "gpt-3.5-turbo": "data/gpt-3.5-turbo"
    },
    "LLM_MODELS": {
        "llama3.1": {   
            "llm": "Ollama",
            "embedding": "OllamaEmbeddings",
            "embedding_model": "mxbai-embed-large",
            "model_name": "llama3.1"
        },
        # "gpt-3.5-turbo": {     
        #     "embedding": "OpenAIEmbeddings",
        #     "embedding_model": "text-embedding-3-small",
        #     "model_name": "gpt-3.5-turbo"
        # }
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