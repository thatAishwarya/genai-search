from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EmbeddingHandler:
    def __init__(self, documents):
        self.documents = documents
        self.doc_ids, self.page_texts, self.embeddings = self._create_embeddings()
        self.index = self._build_faiss_index()

    def _create_embeddings(self):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        doc_ids = []
        page_texts = []
        embeddings = []

        for doc_id, pages in self.documents.items():
            for page_num, text in pages.items():
                doc_ids.append(f"{doc_id} (Page {page_num + 1})")
                page_texts.append(text)
                embeddings.append(model.encode(text, convert_to_tensor=True).cpu().numpy())

        return doc_ids, page_texts, np.array(embeddings)

    def _build_faiss_index(self):
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings)
        return index

    def retrieve_documents(self, query, model, top_k=3):
        query_embedding = model.encode([query], convert_to_tensor=True).cpu().numpy()
        distances, indices = self.index.search(query_embedding, top_k)
        return [(self.doc_ids[i], self.page_texts[i]) for i in indices[0]]
