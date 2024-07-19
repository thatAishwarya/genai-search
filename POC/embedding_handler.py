from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from typing import List

class EmbeddingHandler:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
    
    def create_index(self, dimensions: int):
        self.index = faiss.IndexFlatL2(dimensions)  # Initialize the index with the appropriate dimensionality

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

def save_embeddings(embedding_handler: EmbeddingHandler, path: str):
    with open(path, 'wb') as f:
        pickle.dump(embedding_handler, f)

def load_embeddings(path: str) -> EmbeddingHandler:
    with open(path, 'rb') as f:
        return pickle.load(f)
