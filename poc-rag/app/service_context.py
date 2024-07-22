class ServiceContext:
    def __init__(self, summarizer_model, embedding_indexer):
        self.summarizer_model = summarizer_model  # Updated to use summarizer_model
        self.embedding_indexer = embedding_indexer

    def handle_query(self, query):
        search_results = self.embedding_indexer.query_index(query)
        top_result = search_results[0] if search_results else ("No results", [])
        document_references = [doc for doc in top_result[1]]
        # Combine document references into a single string for summarization
        combined_text = " ".join(document_references)
        summary = self.summarizer_model.summarize_text(combined_text)  # Updated method call
        suggested_queries = self.generate_suggested_queries(query)
        return summary, document_references, suggested_queries

    def generate_suggested_queries(self, query):
        # Placeholder for generating suggested queries
        # Implement your logic here to generate suggestions based on the query
        return [
            f"Related query 1 to '{query}'",
            f"Related query 2 to '{query}'",
        ]
