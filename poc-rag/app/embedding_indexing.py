import logging
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
import faiss
import numpy as np
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingIndexer:
    def __init__(self, chunk_size=1, batch_size=100):
        logger.info("Initializing embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorstore = None
        self.chunk_size = chunk_size
        self.batch_size = batch_size
        logger.info("Embedding model initialized.")

    def preprocess_text(self, text):
        return re.sub(r'[^a-zA-Z0-9\s]', '', text)

    def create_index(self, documents):
        logger.info("Creating index...")
        try:
            chunks = []
            for doc_id, page_number, text in documents:
                if text.strip():  # Ensure that we are processing non-empty text
                    chunks.append((doc_id, page_number, text))  # Each chunk corresponds to a page

            texts = [chunk[2] for chunk in chunks]
            if not texts:
                raise ValueError("No valid text chunks found for embedding.")

            logger.info(f"Encoding {len(texts)} document chunks...")

            dimension = self.embedding_model.get_sentence_embedding_dimension()
            if dimension <= 0:
                raise ValueError("Invalid embedding dimension.")

            index = faiss.IndexFlatL2(dimension)
            def embedding_function(texts):
                return self.embedding_model.encode(texts, convert_to_numpy=True)

            docstore = {(doc_id, page_number): text for doc_id, page_number, text in chunks}
            index_to_docstore_id = {i: (chunks[i][0], chunks[i][1]) for i in range(len(texts))}
            
            self.vectorstore = FAISS(
                embedding_function=embedding_function,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )

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

            embeddings = [embedding for _, embedding in text_embeddings]
            batch_size = self.batch_size
            for i in range(0, len(embeddings), batch_size):
                batch_embeddings = np.array(embeddings[i:i + batch_size])
                try:
                    logger.info(f"Adding batch {i // batch_size + 1}/{len(embeddings) // batch_size + 1} to the index with {len(batch_embeddings)} embeddings...")
                    self.vectorstore.index.add(batch_embeddings)
                    logger.info(f"Successfully added batch {i // batch_size + 1}/{len(embeddings) // batch_size + 1} to the index.")
                except Exception as e:
                    logger.error(f"An error occurred while adding batch {i // batch_size + 1}/{len(embeddings) // batch_size + 1}: {e}")
                    raise

            logger.info("All embeddings added to the index.")
        except Exception as e:
            logger.error(f"An error occurred while creating the index: {e}")
            raise

    def query_index(self, query):
        logger.info(f"Querying index for: {query}")
        try:
            query = self.preprocess_text(query)
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            
            distances, indices = self.vectorstore.index.search(query_embedding, k=5)  # Number of nearest neighbors
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                doc_id, page_number = self.vectorstore.index_to_docstore_id[idx]
                chunk_text = self.vectorstore.docstore[(doc_id, page_number)]
                results.append((distance, doc_id, page_number, chunk_text))

            # Format results
            results_formatted = [
                {
                    "file_name": result[1],
                    "page_number": result[2],
                    "distance": result[0],
                    "chunk_text": result[3]
                }
                for result in results
            ]

            logger.info("Query completed.")
            return results_formatted
        except Exception as e:
            logger.error(f"An error occurred during querying: {e}")
            raise
