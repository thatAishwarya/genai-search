from typing import List, Dict
import numpy as np
from embedding_handler import EmbeddingHandler

class QueryHandler:
    def __init__(self, texts: List[Dict[str, str]]):
        self.texts = texts
        self.embedding_handler = EmbeddingHandler()
        
        # Prepare texts for embedding and initialize index
        text_contents = [text['text'] for text in texts]
        self.embedding_handler.initialize_index(text_contents)

    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        # Generate query embedding
        query_embedding = self.embedding_handler.create_embeddings([query])
        indices = self.embedding_handler.search_index(query_embedding, k)

        # Return the top k contexts
        return [self.texts[i] for i in indices]
