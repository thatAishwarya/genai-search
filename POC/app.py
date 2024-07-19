from flask import Flask, request, jsonify, render_template
from document_handler import read_documents_from_directory, extract_text
from query_handler import QueryHandler
from response_generator import ResponseGenerator
from embedding_handler import EmbeddingHandler
import os

app = Flask(__name__)

# Paths
documents_path = '../Data/Ireland'
index_path = 'index_file.index'

# Initialize components
if os.path.exists(index_path):
    query_handler = QueryHandler(index_path)
else:
    # Create a new index from scratch
    embedding_handler = EmbeddingHandler()
    embedding_handler.create_index(dimensions=384)  # Dimensionality of the embeddings
    documents = read_documents_from_directory(documents_path)  # Read all documents
    embedding_handler.index_documents(documents)
    embedding_handler.save_index(index_path)
    query_handler = QueryHandler(index_path)

response_generator = ResponseGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    query = request.form.get('query')
    document_indices = query_handler.handle_query(query)
    
    # Retrieve document paths from the directory
    document_files = [os.path.join(documents_path, file) for file in os.listdir(documents_path)]
    responses = []
    
    for idx in document_indices:
        doc_path = document_files[idx]
        context = extract_text(doc_path)
        response = response_generator.generate_response(context, query)
        responses.append({'document': doc_path, 'response': response})
    
    return jsonify(responses)

if __name__ == '__main__':
    app.run(debug=True)
