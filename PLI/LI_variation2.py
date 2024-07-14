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
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import AutoMergingRetriever

loader = PyMuPDFReader()
documents = loader.load_data("PLI/base_data/COMPS-1883.pdf")

doc_text = "\n\n".join([d.get_content() for d in documents]) #loader treats each page as a separate document so this is necessary
docs = [Document(text = doc_text)]

node_parser = HierarchicalNodeParser.from_defaults()
nodes = node_parser.get_nodes_from_documents(docs)
print("initial nodes: ",len(nodes))

leaf_nodes = get_leaf_nodes(nodes)
print("initial leaf_nodes: ", len(leaf_nodes))

docstore = SimpleDocumentStore()

docstore.add_documents(nodes)

storage_context = StorageContext.from_defaults(docstore=docstore)

my_llm = Ollama(model = "llama3")

huggingface_embedding = HuggingFaceEmbedding(model_name = "BAAI/bge-base-en-v1.5")

base_index = VectorStoreIndex(leaf_nodes, storage_context = storage_context, llm = my_llm, embed_model = huggingface_embedding)

base_retriever = base_index.as_retriever(similarity_top_k = 6)
retriever = AutoMergingRetriever(base_retriever, storage_context, verbose = True)

query_str = ("In the Sarbanes-Oxley Act of 2002, What body is responsible for establishing the budget for each fiscal year?")

nodes = retriever.retrieve(query_str)
base_nodes = base_retriever.retrieve(query_str)

print("retrieved nodes: ", len(nodes))
print("retrieved base nodes: ", len(base_nodes))

for node in nodes:
    print(node.text[:500])

for node in base_nodes:
    print(node.text[:500])