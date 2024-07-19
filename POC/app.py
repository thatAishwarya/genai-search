from flask import Flask, request, jsonify, render_template
from document_handler import extract_text_from_directory
from query_handler import QueryHandler
from response_generator import ResponseGenerator
import os

app = Flask(__name__)

# Configuration
DATA_DIR = '../Data/Ireland'
response_generator = ResponseGenerator()

# Extract documents
text_data = extract_text_from_directory(DATA_DIR)

# Query Handler
query_handler = QueryHandler(text_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    contexts = query_handler.search(query)
    response = response_generator.generate_response(contexts, query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
