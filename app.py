from fastapi import FastAPI
from data.create_embeddings import get_chat_response

app = FastAPI()

@app.post("/api/chat")
async def chat(query: str):
    response, citations = get_chat_response(query)
    return {"response": response, "citations": citations}