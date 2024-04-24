import openai
import os
from configs.config import oaikey
import time


# openai client
os.environ["OPENAI_API_KEY"] = oaikey
openai.api_key = oaikey

# defining oai sota model for embedddings
embed_model = "text-embedding-ada-002"

def embed(batch: list[str]) -> list[float]:
    # create embeddings (exponential backoff to avoid RateLimitError)
    for j in range(5):  # max 5 retries
        try:
            res = openai.embeddings.create(
                input=batch,
                model=embed_model
            )
            passed = True
        except openai.RateLimitError as e:
            print(f"Rate limit exceeded: {str(e)}")
            time.sleep(2**j)  # wait 2^j seconds before retrying
            print("Retrying...")
    if not passed:
        raise RuntimeError("Failed to create embeddings.")
    # get embeddings
    embeds = [record.embedding for record in res.data]
    return embeds