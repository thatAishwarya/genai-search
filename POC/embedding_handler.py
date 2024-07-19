from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List

class EmbeddingHandler:
    def __init__(self):
        # Initialize the model for generating embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        # Generate embeddings for the texts
        return self.model.encode(texts, convert_to_numpy=True)
    
    def build_index(self, embeddings: np.ndarray):
        # Build the FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
    
    def search_index(self, query_embedding: np.ndarray, k: int = 5) -> List[int]:
        # Search the FAISS index
        distances, indices = self.index.search(query_embedding, k)
        return indices[0].tolist()

    def initialize_index(self, texts: List[str]):
        # Create embeddings and build index
        embeddings = self.create_embeddings(texts)
        self.build_index(embeddings)
