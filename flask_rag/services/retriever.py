"""Vector retrieval service using pgvector."""
from sqlalchemy import text
from models import SessionLocal, Chunk, Document
from config import Config
from services.embedder import embed_query


def retrieve(query: str, top_k: int = Config.TOP_K) -> list[dict]:
    """Retrieve the most relevant chunks for a query.

    After vector search, also pulls in page-1 (declarations) chunks from each
    matched document so the LLM has access to coverage limits and dollar amounts
    that typically live on the declarations page.
    """
    query_embedding = embed_query(query)

    session = SessionLocal()
    try:
        # 1. Vector similarity search
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

        chunks = [
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

        if not chunks:
            return chunks

        # 2. Pull declarations page (page 1) chunks from matched documents
        #    so the LLM has coverage limits and dollar amounts
        matched_doc_ids = {c["document_id"] for c in chunks}
        seen_chunk_ids = {c["chunk_id"] for c in chunks}

        decl_results = session.execute(
            text("""
                SELECT
                    c.id,
                    c.content,
                    c.page_number,
                    c.chunk_index,
                    c.document_id,
                    d.filename,
                    d.title
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                WHERE c.document_id = ANY(:doc_ids)
                  AND c.page_number = 1
                ORDER BY c.document_id, c.chunk_index
            """),
            {"doc_ids": list(matched_doc_ids)},
        )

        for row in decl_results:
            if row.id not in seen_chunk_ids:
                chunks.append({
                    "chunk_id": row.id,
                    "content": row.content,
                    "page_number": row.page_number,
                    "chunk_index": row.chunk_index,
                    "document_id": row.document_id,
                    "filename": row.filename,
                    "title": row.title or row.filename,
                    "similarity": 1.0,  # declarations pages are always relevant context
                })
                seen_chunk_ids.add(row.id)

        return chunks
    finally:
        session.close()
