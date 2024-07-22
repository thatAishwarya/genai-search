import openai
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def search_and_generate_answer(query):
    """
    Search for documents based on a query and generate an answer using OpenAI.
    """
    from search_utils import search_client
    from embeddings import generate_embeddings

    query_embedding = generate_embeddings(query)
    vector_query = {
        "vector": {
            "value": query_embedding.tolist(),
            "fields": ["embedding"]
        },
        "top": 5
    }
    results = search_client.search(search_text="", vectors=[vector_query])
    
    context = "\n".join([result['content'] for result in results])
    
    prompt = f"Given the following context, answer the query: '{query}'\n\nContext:\n{context}\n\nAnswer:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    answer = response.choices[0].text.strip()
    return answer, results
