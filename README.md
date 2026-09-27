# Insurance RAG

A Retrieval-Augmented Generation (RAG) system for insurance policy documents. Upload insurance PDFs, index them into a vector database, and ask natural language questions with cited answers.

## Architecture

**Two-service design** — Django as the system of record, Flask as the RAG microservice.

```
┌─────────────────────────────┐      ┌──────────────────────────┐
│  Django (port 8000)         │      │  Flask RAG (port 5001)   │
│                             │      │                          │
│  • Document management UI   │─────▶│  POST /ingest            │
│  • Admin panel              │      │  POST /query             │
│  • Audit/governance logging │      │  POST /eval              │
│  • User auth                │      │  GET  /health            │
│  • Query interface          │      │                          │
└──────────┬──────────────────┘      └────────┬─────────────────┘
           │                                  │
           │         ┌────────────────────┐   │
           └────────▶│  PostgreSQL + pgvector  │◀──┘
                     │  • Document metadata    │
                     │  • Vector embeddings     │
                     │  • Audit logs            │
                     │  • Golden Q&A set        │
                     └────────────────────┘
```

**Why two frameworks?**
- **Django** — batteries-included admin, auth, ORM, and templating for the enterprise management layer.
- **Flask** — minimal and focused for a narrow, fast RAG API with three endpoints.

## Tech Stack

- **Python 3.12**
- **Flask** — RAG microservice (ingest, query, eval)
- **Django** — document management, admin, audit logging, UI
- **PostgreSQL + pgvector** — relational data + vector similarity search
- **OpenAI API** — embeddings (`text-embedding-3-small`) and generation (`gpt-4o-mini`)
- **PyMuPDF** — PDF text extraction
- **Docker Compose** — full stack orchestration

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/ichandan2151/insurance-rag.git
cd insurance-rag
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Start services

```bash
docker compose up --build
```

This starts PostgreSQL (with pgvector), the Flask RAG service (port 5001), and Django (port 8000).

### 3. Initialize the database

```bash
# Django migrations
docker compose exec django python manage.py migrate

# Create admin user
docker compose exec django python manage.py createsuperuser

# Initialize Flask RAG tables
docker compose exec flask-rag python -c "from models import init_db; init_db()"
```

### 4. Generate sample data and ingest

```bash
# Generate sample insurance PDFs (run from host with PyMuPDF installed)
pip install PyMuPDF
python3 sample_data/generate_sample_pdfs.py

# Ingest into the RAG service
curl -X POST http://localhost:5001/ingest -F "file=@sample_data/homeowners_policy.pdf" -F "title=Homeowners Policy HO-3"
curl -X POST http://localhost:5001/ingest -F "file=@sample_data/auto_insurance_policy.pdf" -F "title=Auto Insurance Policy"
curl -X POST http://localhost:5001/ingest -F "file=@sample_data/term_life_policy.pdf" -F "title=Term Life Policy"

# Seed golden Q&A set for evaluations
docker compose exec flask-rag python seed_golden_set.py
```

### 5. Use

- **Django UI**: http://localhost:8000 — upload documents, ask questions, view audit logs
- **Django Admin**: http://localhost:8000/admin/ — manage documents and review audit trail
- **Flask API**: http://localhost:5001 — direct API access

## Flask RAG API

### `POST /ingest`
Upload and index a PDF document.
```bash
curl -X POST http://localhost:5001/ingest \
  -F "file=@policy.pdf" \
  -F "title=My Policy"
```

### `POST /query`
Ask a question with cited answers.
```bash
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the bodily injury liability limit?", "top_k": 8}'
```

### `POST /eval`
Run the golden-set evaluation harness.
```bash
curl -X POST http://localhost:5001/eval \
  -H "Content-Type: application/json" \
  -d '{"top_k": 8}'
```

## RAG Pipeline

1. **Ingest** — PDF text extraction (PyMuPDF) → sentence-based chunking with overlap → OpenAI embeddings → stored in pgvector
2. **Retrieve** — query embedding → cosine similarity search via pgvector → declarations page augmentation (automatically includes page 1 from matched documents for coverage limits/amounts)
3. **Generate** — retrieved chunks passed as context to GPT-4o-mini with citation instructions → cited answer returned

## Evaluation

The eval harness (`/eval` endpoint) runs queries from a golden Q&A set and measures:
- **Keyword overlap** — rough faithfulness proxy between generated and expected answers
- **Retrieval precision** — percentage of questions where a chunk scores above 0.7 similarity
- **Average retrieval similarity** — mean cosine similarity of retrieved chunks

Golden set includes 12 Q&A pairs across homeowners, auto, and term life policies.

## Project Structure

```
insurance-rag/
├── flask_rag/                 # RAG microservice
│   ├── app.py                 # Flask app — /ingest, /query, /eval
│   ├── config.py              # Environment-based configuration
│   ├── models/database.py     # SQLAlchemy models + pgvector
│   ├── services/
│   │   ├── chunker.py         # PDF extraction + chunking
│   │   ├── embedder.py        # OpenAI embeddings
│   │   ├── retriever.py       # pgvector search + declarations augmentation
│   │   └── generator.py       # LLM answer generation with citations
│   ├── seed_golden_set.py     # Load golden Q&A into DB
│   ├── tests/                 # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── django_app/                # Enterprise management layer
│   ├── insurance_project/     # Django project settings
│   ├── documents/             # Main app — models, views, admin, templates
│   │   ├── models.py          # PolicyDocument, AuditLog
│   │   ├── views.py           # Dashboard, upload, query, audit
│   │   ├── admin.py           # Admin panel config
│   │   ├── rag_client.py      # HTTP client for Flask service
│   │   └── templates/
│   ├── Dockerfile
│   └── requirements.txt
├── sample_data/               # Sample insurance PDFs + golden set
│   ├── generate_sample_pdfs.py
│   └── golden_set.json
├── docker-compose.yml
└── .env.example
```
