from llama_index.readers.file import PDFReader
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    SentenceSplitter,
    get_leaf_nodes,
    get_root_nodes,
)
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.llms.ollama import Ollama

loader = PyMuPDFReader()
documents = loader.load_data("PLI/base_data/Transfer_Pricing.pdf")

doc_text = "\n\n".join([d.get_content() for d in documents]) #loader treats each page as a separate document so this is necessary
docs = [Document(text = doc_text)]

node_parser = HierarchicalNodeParser.from_defaults()
nodes = node_parser.get_nodes_from_documents(docs)
print(len(nodes))

leaf_nodes = get_leaf_nodes(nodes)
print(len(leaf_nodes))

docstore = SimpleDocumentStore()

storage_context = StorageContext.from_defaults(docstore=docstore)

my_llm = Ollama(model = "llama3")

base_index = VectorStoreIndex(leaf_nodes, storage_context = storage_context, llm = my_llm, embed_model = 'local', model_name = "llama3")