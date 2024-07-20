from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List

class EmbeddingHandler2:
    def __init__(self, model_name: str, llama_type: str):
        self.model_name = model_name
        self.type = llama_type

        if self.type == 'default':
            self.model = SentenceTransformer(model_name)
        elif self.type == 'huggingface':
            self.model = HuggingFaceEmbedding(model_name)

        self.index = None
    
    def create_index(self, dimensions: int):
        if self.type == 'default':
            self.index = faiss.IndexFlatL2(dimensions)
        if self.type == 'huggingface'  # Initialize the index with the appropriate dimensionality

    def index_documents(self, documents: List[str]):
        embeddings = self.model.encode(documents)
        self.index.add(embeddings)
        
    def save_index(self, path: str):
        faiss.write_index(self.index, path)

    def load_index(self, path: str):
        self.index = faiss.read_index(path)

    def query(self, query: str, k: int = 5) -> List[int]:
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, k)
        return indices[0]

def save_embeddings(embedding_handler: EmbeddingHandler2, path: str):
    with open(path, 'wb') as f:
        pickle.dump(embedding_handler, f)

def load_embeddings(path: str) -> EmbeddingHandler2:
    with open(path, 'rb') as f:
        return pickle.load(f)
