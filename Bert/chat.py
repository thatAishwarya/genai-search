from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from document_handler import DocumentHandler
from embedding_handler import EmbeddingHandler
from response_generator import ResponseGenerator
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)
CORS(app)

folder_path = '../Data/Ireland'
doc_handler = DocumentHandler(folder_path)
documents = doc_handler.get_documents()
embedding_handler = EmbeddingHandler(documents)
model = SentenceTransformer('all-MiniLM-L6-v2')
response_generator = ResponseGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data['query']
    retrieved_docs = embedding_handler.retrieve_documents(query, model)
    results = [{
        "document": doc_info,
        "summary": response_generator.generate_summary(context),
        "page": doc_info.split(" (Page ")[-1][:-1],
        "path": os.path.join(folder_path, doc_info.split(" (Page ")[0])
    } for doc_info, context in retrieved_docs]
    
    return jsonify(results)

@app.route('/view/<path:filename>/<int:page>')
def view_document(filename, page):
    return render_template('viewer.html', file_path=filename, page=page)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(folder_path, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
