"""Embedding service using OpenAI."""
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Batches requests to stay within API limits.
    """
    embeddings = [


        
    ]
    batch_size = 100  # OpenAI limit is 2048, but 100 is safe for large chunks

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=Config.EMBEDDING_MODEL,
        )
        embeddings.extend([item.embedding for item in response.data])

    return embeddings


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    response = client.embeddings.create(
        input=[query],
        model=Config.EMBEDDING_MODEL,
    )
    return response.data[0].embedding
