"""Insurance RAG Microservice — Flask API."""
import os
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from config import Config
from models import init_db, SessionLocal, Document, Chunk, GoldenQA
from services.chunker import extract_text_from_pdf, chunk_text
from services.embedder import embed_texts
from services.retriever import retrieve
from services.generator import generate_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "insurance-rag"})


# ---------------------------------------------------------------------------
# POST /ingest — Upload, chunk, embed, and store a PDF
# ---------------------------------------------------------------------------
@app.route("/ingest", methods=["POST"])
def ingest():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Send a PDF as 'file'."}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    filename = secure_filename(file.filename)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    session = SessionLocal()
    try:
        # 1. Create document record
        doc = Document(filename=filename, title=request.form.get("title", filename))
        session.add(doc)
        session.flush()  # get doc.id
        logger.info(f"Ingesting document {doc.id}: {filename}")

        # 2. Extract text and chunk
        pages = extract_text_from_pdf(filepath)
        doc.page_count = len(pages)
        chunks = chunk_text(pages)
        logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")

        # 3. Embed all chunks
        texts = [c.content for c in chunks]
        embeddings = embed_texts(texts)

        # 4. Store chunks with embeddings
        for chunk_result, embedding in zip(chunks, embeddings):
            chunk = Chunk(
                document_id=doc.id,
                chunk_index=chunk_result.chunk_index,
                content=chunk_result.content,
                page_number=chunk_result.page_number,
                embedding=embedding,
            )
            session.add(chunk)

        doc.status = "indexed"
        session.commit()
        logger.info(f"Document {doc.id} indexed successfully")

        return jsonify({
            "document_id": doc.id,
            "filename": filename,
            "pages": doc.page_count,
            "chunks": len(chunks),
            "status": "indexed",
        }), 201

    except Exception as e:
        session.rollback()
        logger.error(f"Ingest failed: {e}")
        # Update status to failed if doc was created
        try:
            if doc.id:
                doc.status = "failed"
                session.commit()
        except Exception:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


# ---------------------------------------------------------------------------
# POST /query — Retrieve relevant chunks and generate a cited answer
# ---------------------------------------------------------------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Provide a JSON body with 'question'."}), 400

    question = data["question"]
    top_k = data.get("top_k", Config.TOP_K)

    try:
        # 1. Retrieve relevant chunks
        chunks = retrieve(question, top_k=top_k)

        if not chunks:
            return jsonify({
                "answer": "No relevant documents found. Please ingest insurance policy documents first.",
                "sources": [],
            })

        # 2. Generate answer with citations
        result = generate_answer(question, chunks)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Query failed: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /eval — Run golden-set evaluation harness
# ---------------------------------------------------------------------------
@app.route("/eval", methods=["POST"])
def eval_harness():
    """Run evaluation against golden Q&A set.

    Accepts optional JSON body:
      - top_k: number of chunks to retrieve (default: Config.TOP_K)
      - golden_set: optional inline list of {"question", "expected_answer"} dicts
                    (if omitted, uses golden_qa table in DB)
    """
    data = request.get_json() or {}
    top_k = data.get("top_k", Config.TOP_K)

    # Load golden set — from request body or database
    if "golden_set" in data:
        golden_set = data["golden_set"]
    else:
        session = SessionLocal()
        try:
            rows = session.query(GoldenQA).all()
            golden_set = [
                {"question": r.question, "expected_answer": r.expected_answer}
                for r in rows
            ]
        finally:
            session.close()

    if not golden_set:
        return jsonify({"error": "No golden set found. Add entries to golden_qa table or pass in request body."}), 400

    results = []
    total_similarity = 0.0
    retrieval_hits = 0

    for item in golden_set:
        question = item["question"]
        expected = item["expected_answer"]

        try:
            chunks = retrieve(question, top_k=top_k)
            answer_result = generate_answer(question, chunks)

            # Simple evaluation metrics
            answer_lower = answer_result["answer"].lower()
            expected_lower = expected.lower()

            # Keyword overlap as a rough faithfulness proxy
            expected_keywords = set(expected_lower.split())
            answer_keywords = set(answer_lower.split())
            keyword_overlap = len(expected_keywords & answer_keywords) / max(len(expected_keywords), 1)

            # Average retrieval similarity
            avg_similarity = (
                sum(c["similarity"] for c in chunks) / len(chunks) if chunks else 0.0
            )
            total_similarity += avg_similarity

            # Check if any chunk is actually relevant (similarity > 0.7)
            has_relevant_chunk = any(c["similarity"] > 0.7 for c in chunks)
            if has_relevant_chunk:
                retrieval_hits += 1

            results.append({
                "question": question,
                "expected_answer": expected,
                "generated_answer": answer_result["answer"],
                "keyword_overlap": round(keyword_overlap, 3),
                "avg_retrieval_similarity": round(avg_similarity, 3),
                "has_relevant_chunk": has_relevant_chunk,
                "num_sources": len(answer_result["sources"]),
            })
        except Exception as e:
            results.append({
                "question": question,
                "error": str(e),
            })

    # Aggregate metrics
    n = len(golden_set)
    avg_keyword_overlap = sum(r.get("keyword_overlap", 0) for r in results) / max(n, 1)
    retrieval_precision = retrieval_hits / max(n, 1)

    return jsonify({
        "summary": {
            "total_questions": n,
            "avg_keyword_overlap": round(avg_keyword_overlap, 3),
            "retrieval_precision": round(retrieval_precision, 3),
            "avg_retrieval_similarity": round(total_similarity / max(n, 1), 3),
        },
        "results": results,
    })


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
