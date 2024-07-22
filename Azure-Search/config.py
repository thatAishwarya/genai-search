import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure configuration
SEARCH_SERVICE_NAME = os.getenv("AZURE_SEARCH_SERVICE_NAME")
SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")
BLOB_SERVICE_ENDPOINT = os.getenv("BLOB_SERVICE_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
