import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Postgres + pgvector
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/insurance_rag"
    )

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))

    # Retrieval
    TOP_K = int(os.getenv("TOP_K", "8"))

    # Upload
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/insurance_rag_uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
