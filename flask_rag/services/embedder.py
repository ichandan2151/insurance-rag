"""Embedding service using OpenAI."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

BATCH_SIZE = 100
MAX_EMBED_WORKERS = 4


def _embed_batch(batch: list[str]) -> list[list[float]]:
    """Embed a single batch via the OpenAI API."""
    response = client.embeddings.create(
        input=batch,
        model=Config.EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Splits into batches and processes them concurrently.
    """
    if not texts:
        return []

    batches = [texts[i:i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]

    if len(batches) == 1:
        return _embed_batch(batches[0])

    # Process multiple batches concurrently
    results: dict[int, list[list[float]]] = {}
    with ThreadPoolExecutor(max_workers=MAX_EMBED_WORKERS) as pool:
        futures = {pool.submit(_embed_batch, b): idx for idx, b in enumerate(batches)}
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    # Reassemble in original order
    embeddings = []
    for idx in range(len(batches)):
        embeddings.extend(results[idx])
    return embeddings


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    response = client.embeddings.create(
        input=[query],
        model=Config.EMBEDDING_MODEL,
    )
    return response.data[0].embedding
