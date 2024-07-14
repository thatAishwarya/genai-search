from document_handler import DocumentHandler
from embedding_handler import EmbeddingHandler
from response_generator import ResponseGenerator
from sentence_transformers import SentenceTransformer

def main():
    folder_path = 'Data/Ireland'  # Path to your document folder
    doc_handler = DocumentHandler(folder_path)
    documents = doc_handler.get_documents()

    if not documents:
        print("No documents found in the specified folder.")
        return

    embedding_handler = EmbeddingHandler(documents)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    response_generator = ResponseGenerator()

    while True:
        query = input("Enter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        retrieved_docs = embedding_handler.retrieve_documents(query, model)
        if retrieved_docs:
            for doc_info, context in retrieved_docs:
                summary = response_generator.generate_summary(context)
                print(f"\nDocument: {doc_info}\nSummary: {summary}\n")
        else:
            print("No documents found for your query.")

if __name__ == "__main__":
    main()
