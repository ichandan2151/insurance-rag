"""Vector retrieval service using pgvector."""
from sqlalchemy import text
from models import SessionLocal, Chunk, Document
from config import Config
from services.embedder import embed_query


def retrieve(query: str, top_k: int = Config.TOP_K) -> list[dict]:
    """Retrieve the most relevant chunks for a query."""
    query_embedding = embed_query(query)

    session = SessionLocal()
    try:
        # pgvector cosine distance search
        results = session.execute(
            text("""
                SELECT
                    c.id,
                    c.content,
                    c.page_number,
                    c.chunk_index,
                    c.document_id,
                    d.filename,
                    d.title,
                    1 - (c.embedding <=> :embedding) AS similarity
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE d.status = 'indexed'
                ORDER BY c.embedding <=> :embedding
                LIMIT :top_k
            """),
            {"embedding": str(query_embedding), "top_k": top_k},
        )

        return [
            {
                "chunk_id": row.id,
                "content": row.content,
                "page_number": row.page_number,
                "chunk_index": row.chunk_index,
                "document_id": row.document_id,
                "filename": row.filename,
                "title": row.title or row.filename,
                "similarity": float(row.similarity),
            }
            for row in results
        ]
    finally:
        session.close()
