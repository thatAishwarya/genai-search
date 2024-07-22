import logging
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
import numpy as np
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingIndexer:
    def __init__(self, chunk_size=100, batch_size=100):
        logger.info("Initializing embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorstore = None
        self.chunk_size = chunk_size
        self.batch_size = batch_size
        logger.info("Embedding model initialized.")

    def chunk_text(self, text):
        words = text.split()
        for i in range(0, len(words), self.chunk_size):
            yield " ".join(words[i:i + self.chunk_size])

    def preprocess_text(self, text):
        # Remove special characters and keep alphanumeric characters and spaces
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)

    def create_index(self, documents):
        logger.info("Creating index...")
        try:
            # Create a list of (chunk_id, chunk_text) tuples
            chunks = []
            for doc_id, text in documents:
                text = self.preprocess_text(text)
                for chunk_id, chunk in enumerate(self.chunk_text(text)):
                    if chunk.strip():  # Ensure chunk is not empty
                        chunks.append((doc_id, chunk_id, chunk))
            
            texts = [chunk[2] for chunk in chunks]
            if not texts:
                raise ValueError("No valid text chunks found for embedding.")

            logger.info(f"Encoding {len(texts)} document chunks...")

            dimension = self.embedding_model.get_sentence_embedding_dimension()
            if dimension <= 0:
                raise ValueError("Invalid embedding dimension.")

            index = faiss.IndexFlatL2(dimension)
            def embedding_function(text):
                return self.embedding_model.encode(text, convert_to_numpy=True)

            # Map chunk ids to their original document ids and chunks
            docstore = {(doc_id, chunk_id): chunk for doc_id, chunk_id, chunk in chunks}
            index_to_docstore_id = {i: (chunks[i][0], chunks[i][1]) for i in range(len(texts))}
            
            self.vectorstore = FAISS(
                embedding_function=embedding_function,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )

            # Batch processing for encoding
            text_embeddings = []
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                logger.info(f"Encoding batch {i // self.batch_size + 1}/{len(texts) // self.batch_size + 1}...")
                batch_embeddings = self.embedding_model.encode(batch_texts, convert_to_numpy=True, show_progress_bar=True)
                logger.info(f"Batch {i // self.batch_size + 1} embeddings shape: {batch_embeddings.shape}")
                if batch_embeddings.shape[1] != dimension:
                    raise ValueError("Inconsistent embedding dimensions detected.")
                text_embeddings.extend(zip(batch_texts, batch_embeddings))

            logger.info("All document chunks encoded.")
            logger.info("Adding embeddings to the index in batches...")

            # Batch processing for adding embeddings
            for i in range(0, len(text_embeddings), self.batch_size-1):
                batch_text_embeddings = text_embeddings[i:i + self.batch_size]
                try:
                    logger.info(f"Adding batch {i // self.batch_size + 1}/{len(text_embeddings) // self.batch_size + 1} to the index with {len(batch_text_embeddings)} embeddings...")
                    self.vectorstore.add_embeddings(batch_text_embeddings)
                    logger.info(f"Successfully added batch {i // self.batch_size + 1}/{len(text_embeddings) // self.batch_size + 1} to the index.")
                except Exception as e:
                    logger.error(f"An error occurred while adding batch {i // self.batch_size + 1}/{len(text_embeddings) // self.batch_size + 1}: {e}")
                    raise

            logger.info("All embeddings added to the index.")
        except Exception as e:
            logger.error(f"An error occurred while creating the index: {e}")
            raise

    def query_index(self, query):
        logger.info(f"Querying index for: {query}")
        try:
            query = self.preprocess_text(query)
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            distances, indices = self.vectorstore.search(query_embedding)
            results = []

            for distance, idx in zip(distances[0], indices[0]):
                doc_id, chunk_id = self.vectorstore.index_to_docstore_id[idx]
                chunk_text = self.vectorstore.docstore[(doc_id, chunk_id)]
                results.append((distance, chunk_text))

            logger.info("Query completed.")
            return results
        except Exception as e:
            logger.error(f"An error occurred during querying: {e}")
            raise