from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.ai.formrecognizer import FormRecognizerClient
from azure.storage.blob import BlobServiceClient
from config import SEARCH_SERVICE_NAME, SEARCH_ADMIN_KEY, FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, BLOB_SERVICE_ENDPOINT

# Initialize Azure clients
search_endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
search_client = SearchClient(endpoint=search_endpoint, index_name="vector-search-index", credential=DefaultAzureCredential())
index_client = SearchIndexClient(endpoint=search_endpoint, credential=DefaultAzureCredential())

# Initialize Form Recognizer client
form_recognizer_client = FormRecognizerClient(endpoint=FORM_RECOGNIZER_ENDPOINT, credential=DefaultAzureCredential())

# Initialize Blob Service client
blob_service_client = BlobServiceClient(account_url=BLOB_SERVICE_ENDPOINT, credential=DefaultAzureCredential())
