import logging

# Configure logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Ensure info level logs are captured

class ServiceContext:
    def __init__(self, summarizer_model, embedding_indexer):
        self.summarizer_model = summarizer_model
        self.embedding_indexer = embedding_indexer
        logger.info("ServiceContext initialized with summarizer_model and embedding_indexer.")

    def handle_query(self, query):
        logger.info(f"Handling query: {query}")
        try:
            search_results = self.embedding_indexer.query_index(query)
            logger.info(f"Search results obtained: {search_results}")

            if not search_results:
                return "No relevant information found.", [], []

            # Sort search results by relevance (distance)
            search_results = sorted(search_results, key=lambda x: x['distance'])

            # Combine relevant chunks to form a comprehensive context for summarization
            combined_text = " ".join(result['chunk_text'] for result in search_results[:5])  # Use top 5 results for context
            logger.info(f"Combined text for summarization: {combined_text[:500]}...")  # Log a snippet

            # Generate summary
            summary = self.summarizer_model.summarize_text(combined_text)
            logger.info(f"Generated summary: {summary}")

            # Prepare document references
            document_references = [
                {
                    "file_name": result['file_name'],
                    "page_number": result['page_number']
                }
                for result in search_results
            ]

            # Generate suggested queries
            suggested_queries = self.generate_suggested_queries(query)
            logger.info(f"Suggested queries: {suggested_queries}")

            return summary, document_references, suggested_queries
        except Exception as e:
            logger.error(f"An error occurred while handling the query: {e}")
            raise

    def generate_suggested_queries(self, query):
        logger.info(f"Generating suggested queries for: {query}")
        suggestions = [
            f"Related query 1 to '{query}'",
            f"Related query 2 to '{query}'",
        ]
        logger.info(f"Suggested queries generated: {suggestions}")
        return suggestions
