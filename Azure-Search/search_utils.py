from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import ComplexField, SearchFieldDataType, SimpleField, SearchIndex
from azure.search.documents.models import IndexDocumentsBatch, IndexAction
from config import SEARCH_SERVICE_NAME, SEARCH_ADMIN_KEY

# Initialize SearchIndexClient
from azure.identity import DefaultAzureCredential
search_endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
index_client = SearchIndexClient(endpoint=search_endpoint, credential=DefaultAzureCredential())

def create_search_index():
    """
    Create a search index in Azure Cognitive Search.
    """
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="content", type=SearchFieldDataType.String, searchable=True),
        ComplexField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single))
    ]
    index = SearchIndex(name="vector-search-index", fields=fields)
    index_client.create_index(index)

def upload_documents(documents, embeddings):
    """
    Upload documents and their embeddings to Azure Cognitive Search.
    """
    documents_to_upload = [
        {
            "id": file_name,
            "content": documents[i],
            "embedding": embeddings[i].tolist()
        }
        for i, file_name in enumerate(file_names)
    ]
    batch = IndexDocumentsBatch(actions=[IndexAction.upload(d) for d in documents_to_upload])
    search_client.index_documents(batch=batch)
