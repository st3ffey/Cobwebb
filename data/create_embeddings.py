import openai
from pinecone import Pinecone
import cohere
from configs.config import coherekey, oaikey, pineconekey
#from data.proxies import data

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

#data['id'] = data['id'].astype(str)

batch_size = 100  # how many embeddings im creating and inserting

def embed_data(df, batch_size, model, index):
    for i in tqdm(range(0, len(df), batch_size), desc="Processing batches", unit="batch"):
        passed = False
        i_end = min(len(df), i+batch_size)
        batch = df[i:i_end]
        
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