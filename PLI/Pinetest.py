from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import google

pc = Pinecone(api_key = "99ece196-dd40-4da0-9d90-6c37965d0911")

index_name = "quickstart"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=2,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 

index = pc.Index(index_name)

index.upsert(
    vectors=[
        {"id": "vec1", "values": [1.0, 1.5]},
        {"id": "vec2", "values": [2.0, 1.0]},
        {"id": "vec3", "values": [0.1, 3.0]},
    ],
    namespace="ns1"
)

index.upsert(
    vectors=[
        {"id": "vec1", "values": [1.0, -2.5]},
        {"id": "vec2", "values": [3.0, -2.0]},
        {"id": "vec3", "values": [0.5, -1.5]},
    ],
    namespace="ns2"
)

query_results1 = index.query(
    namespace = "ns2",
    vector = [1.0, 1.5],
    top_k = 3,
    include_values = True
)

print(query_results1)

pc.delete_index(index_name)

### Result:
#{'matches': [{'id': 'vec2',
#             'metadata': None,
#             'score': 0.0,
#              'sparse_values': {'indices': [], 'values': []},
#              'values': [3.0, -2.0]},
#             {'id': 'vec1',
#              'metadata': None,
#              'score': -0.56652886,
#              'sparse_values': {'indices': [], 'values': []},
#              'values': [1.0, -2.5]},
#             {'id': 'vec3',
#              'metadata': None,
#              'score': -0.6139406,
#              'sparse_values': {'indices': [], 'values': []},
#              'values': [0.5, -1.5]}],
# 'namespace': 'ns2',
# 'usage': {'read_units': 6}}