from src.embeddings import embed, co
from configs.config import index
import openai

# Initialize the conversation history
conversation_history = []

def get_docs(query: str, top_k: int):
    # encode query
    xq = embed([query])[0]

    # search pinecone index
    res = index.query(vector=xq, top_k=top_k, include_metadata=True)

    # extract chunk_text and metadata separately
    docs = []
    for i, x in enumerate(res["matches"]):
        chunk_text = x.metadata["chunk_test"]
        metadata = {k: v for k, v in x.metadata.items() if k != "chunk_test"}
        docs.append({"chunk_text": chunk_text, "metadata": metadata})
    
    return docs

def generate_response(query, docs, metadata, citations, conversation_history):
    # Combine the conversation history into a single string
    history_string = "\n".join([f"User: {user_query}\nAssistant: {assistant_response}" for user_query, assistant_response in conversation_history])

    response = openai.chat.completions.create(
        model='gpt-4-1106-preview',
        temperature=0.05,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant, meant to provide an answer to the user \
            question. If the user asks for company names and they aren't available in the text, provide the ticker."},
            {"role": "user", "content": f"Conversation history:\n{history_string}\n\nQuery: {query}\nDocs, in a list: {docs}, and metadata: {metadata}"}
        ]
    )
    return response.choices[0].message.content

def generate_alternative_question(query):
    prompt = f"Given the question: '{query}', generate an alternative question that conveys the same meaning \
    or information need. Only respond with the question you've created. Nothing else."

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        temperature=0.05,
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    )

    alternative_question = response.choices[0].message.content
    return alternative_question

def get_chat_response(query, top_k=25, top_n=8):
    # Generate alternative question
    alternative_question = generate_alternative_question(query)
    
    # Combine the original query and alternative question
    expanded_query = query + ". In other terms," + alternative_question
    print(expanded_query)
    
    # Perform document retrieval using the expanded query
    docs = get_docs(expanded_query, top_k=top_k)
    
    # Extract chunk_text and metadata from the retrieved documents
    documents = [doc["chunk_text"] for doc in docs]
    metadata = [doc["metadata"] for doc in docs]
    
    # Rerank the documents
    rerank_docs = co.rerank(
        query=query,
        documents=documents,
        top_n=top_n,
        model="rerank-english-v2.0"
    )
    reranked_candidates = rerank_docs.results
    
    # Get the reranked document content and metadata
    doc_content = [documents[candidate.index] for candidate in reranked_candidates]
    doc_metadata = [metadata[candidate.index] for candidate in reranked_candidates]
    
    # Generate citations for the reranked documents
    citations = "\n".join([f"{i+1}. {doc}\nMetadata: {doc_metadata[i]}" for i, doc in enumerate(doc_content)])
    
    # Generate a response based on the reranked documents and conversation history
    response = generate_response(query, doc_content, doc_metadata, citations, conversation_history)
    
    # Append the user's query and the model's response to the conversation history
    conversation_history.append((query, response))
    
    return response, citations