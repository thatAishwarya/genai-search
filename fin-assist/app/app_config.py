import logging

# Configuration settings
SETTINGS = {
    "PDF_DIR": "data/TCA",
    "PERSIST_DIRECTORIES": {
        # "llama3.1": "data/llama3.1",
        "llama3.1" : "data/opensource",
        "gpt-3.5-turbo": "data/gpt"
    },
    "LLM_MODELS": {
        "llama3.1": {   
            "llm": "Groq",
            "embedding": "GroqEmbeddings",
            "embedding_model": "sentence-transformers/all-mpnet-base-v2",
            "model_name": "llama-3.1-70b-versatile"
        },
        "gpt-3.5-turbo": {     
            "embedding": "OpenAIEmbeddings",
            "embedding_model": "text-embedding-3-small",
            "model_name": "gpt-3.5-turbo"
        }
    },
    "DEFAULT_MODEL": "llama3.1",
    "LLM_BASE_URL": "http://localhost:11434",
    "PROMPT_TEMPLATE": """You are a knowledgeable chatbot, here to help with questions of the user. Your tone should be professional and informative.
        Context: {context}
        History: {summary_memory}
        User: {question}
        Chatbot:""",
    "LOGGING_LEVEL": logging.DEBUG,
    "OPENAI_API_KEY": "",
    "GROQ_API_KEY": ""
}