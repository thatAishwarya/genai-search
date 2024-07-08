from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("PLI/data").load_data()
index = VectorStoreIndex.from_documents(documents)

query_engine = index.query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)