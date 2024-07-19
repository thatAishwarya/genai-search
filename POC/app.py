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

documents_path = 'Data/TCA'
index_path = 'index_file.index'

class Testoid():
    def __init__(self, documents_path, index_path):

        self.app = Flask(__name__)

        #Exception handling for documents_path
        try:
            x = os.getcwd() #included for getting the current working directory
            self.dp = os.path.join (x, documents_path) #included for normalizing the path
            if not os.path.exists(self.dp):
                raise ValueError(f"Directory {self.dp} does not exist")
        except ValueError as e:
            logger.error(f"Failed to initialize Testoid: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Testoid: {e}")
            raise

        #Exception handling for index_path
        if os.path.exists(index_path):
            self.ip = index_path
            self.qh = QueryHandler(index_path)
        else:         
            # Create a new index from scratch
            embedding_handler = EmbeddingHandler()
            embedding_handler.create_index(dimensions=384)  # Dimensionality of the embeddings
            documents = read_documents_from_directory(self.dp)  # Read all documents

            #Exception handling for missing documents
            try :
                if not documents:
                    raise ValueError("No documents found in the directory")
                else:
                    embedding_handler.index_documents(documents)
            except ValueError as e:
                logger.error(f"Failed to index documents: {e}")
                raise
            except Exception as e:
                logger.error(f"Failed to index documents: {e}")
                raise

            embedding_handler.save_index(index_path)
            self.qh = QueryHandler(index_path)
        
        self.rg = ResponseGenerator()
        self.register_routes()

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
