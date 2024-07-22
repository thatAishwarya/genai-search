from flask import Flask, request, jsonify, render_template
from document_handler import read_documents_from_directory, extract_text
from query_handler import QueryHandler
from response_generator import ResponseGenerator
from embedding_handler import EmbeddingHandler
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

documents_path = 'Data/TCA-Test'
index_path = 'index_file.index'

class Testoid():
    def __init__(self, documents_path, index_path):

        self.app = Flask(__name__)
        self.doc_init(documents_path)
        self.idx_init(index_path)
        self.rg = ResponseGenerator()
        self.register_routes()


    #Exception handling for documents_path    
    def doc_init(self, documents_path):
        try:
            x = os.getcwd()
            self.dp = os.path.join (x, documents_path) 
            if not os.path.exists(self.dp):
                raise ValueError(f"Directory {self.dp} does not exist")
        except ValueError as e:
            logger.error(f"Failed to initialize Testoid: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Testoid: {e}")
            raise
    
    #Initializes Index + Exception handling for index_path
    def idx_init(self, index_path):
        # Check if the index file exists
        if os.path.exists(index_path):
            #reload old index
            self.ip = index_path
            self.qh = QueryHandler(index_path)
        else:         
            # Create a new index from scratch
            self.embedding_handler = EmbeddingHandler()
            self.embedding_handler.create_index(dimensions=384)  # Dimensionality of the embeddings
            self.documents = read_documents_from_directory(self.dp)  # Read all documents

            self.embed_init(index_path)

    #Initializes Embedding + Exception handling for missing documents
    def embed_init(self, index_path):

        try :
            if not self.documents:
                raise ValueError("No documents found in the directory")
            else:
                self.embedding_handler.index_documents(self.documents)
        except ValueError as e:
            logger.error(f"Failed to index documents: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            raise

        self.embedding_handler.save_index(index_path)
        self.qh = QueryHandler(index_path)
        
    def register_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/ask', 'ask', self.ask, methods=['POST'])

    def index(self):
            return render_template('index.html')
        

    def ask(self):
        query = request.form.get('query')
        document_indices = self.qh.handle_query(query)

        # Retrieve document paths from the directory
        document_files = [os.path.join(documents_path, file) for file in os.listdir(self.dp)]
        responses = []
        
        for idx in document_indices:
            doc_path = document_files[idx]
            context = extract_text(doc_path)
            response = self.rg.generate_response(context, query)
            responses.append({'document': doc_path, 'response': response})
        
        return jsonify(responses)

#testoid = Testoid(documents_path, index_path)
#if __name__ == '__main__':
    #testoid.app.run(debug=True)

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

