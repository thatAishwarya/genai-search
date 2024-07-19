from embedding_handler import EmbeddingHandler
from typing import List

class QueryHandler:
    def __init__(self, index_path: str):
        self.embedding_handler = EmbeddingHandler()
        self.embedding_handler.load_index(index_path)
    
    def handle_query(self, query: str) -> List[int]:
        return self.embedding_handler.query(query)
