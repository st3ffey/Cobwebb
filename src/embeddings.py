import openai
from pinecone import Pinecone
import cohere
from configs.config import coherekey, oaikey, pineconekey

import os
import pandas as pd
from tqdm.auto import tqdm
import time

# cohere client
co = cohere.Client(coherekey)

# pinecone client
pc = Pinecone(api_key=pineconekey)
index = pc.Index("2023proxies")

# openai client
os.environ["OPENAI_API_KEY"] = oaikey
openai.api_key = oaikey

# defining oai sota model for embedddings
embed_model = "text-embedding-ada-002"

data = pd.read_csv(r"data\2023proxies.csv")

data['id'] = data['id'].astype(str)

batch_size = 100  # how many embeddings im creating and inserting

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

def embed_data(df, batch_size, model, index):
    for i in tqdm(range(0, len(data), batch_size), desc="Processing batches", unit="batch"):
        passed = False
        i_end = min(len(data), i+batch_size)
        batch = data[i:i_end]
        
        for j in range(5):
            try:
                res = openai.embeddings.create(input=batch["text"], model=model)
                passed = True
                break
            except openai.RateLimitError:
                time.sleep(2**j)
                print("Retrying...")
        
        if not passed:
            raise RuntimeError("Failed to create embeddings.")
        
        embeds = [record.embedding for record in res.data]
        to_upsert = list(zip(batch["id"], embeds, batch["metadata"]))
        index.upsert(vectors=to_upsert)
        
        print(f'Embedded {i+len(batch)} vectors!')