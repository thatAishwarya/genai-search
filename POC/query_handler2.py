
from embedding_handler2 import EmbeddingHandler2
from typing import List

class QueryHandler:
    def __init__(self, index_path: str):
        self.embedding_handler = EmbeddingHandler2("BAAI/bge-small-en-v1.5", "huggingface")
        self.embedding_handler.load_index(index_path)
    
    def handle_query(self, query: str) -> List[int]:
        return self.embedding_handler.query(query)
