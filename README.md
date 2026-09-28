# Insurance RAG

A Retrieval-Augmented Generation (RAG) system for insurance policy documents. Upload insurance PDFs, index them into a vector database, and ask natural language questions with cited answers.

## Architecture

**Three-tier design** — React SPA frontend, Django as the system of record, Flask as the RAG microservice.

```
┌──────────────────────┐
│  React (port 3001)   │
│                      │
│  • Modern SPA UI     │
│  • Dashboard         │
│  • Document mgmt     │──────┐
│  • Query interface   │      │
│  • Audit log viewer  │      │
└──────────────────────┘      │
                              ▼
┌─────────────────────────────────────┐      ┌──────────────────────────┐
│  Django (port 8000)                 │      │  Flask RAG (port 5001)   │
│                                     │      │                          │
│  • REST API for React frontend      │─────▶│  POST /ingest            │
│  • Admin panel                      │      │  POST /query             │
│  • Audit/governance logging         │      │  POST /eval              │
│  • User auth & sessions             │      │  GET  /health            │
│  • Document management              │      │                          │
└──────────┬──────────────────────────┘      └────────┬─────────────────┘
           │                                          │
           │         ┌──────────────────────────┐     │
           └────────▶│  PostgreSQL + pgvector    │◀───┘
                     │  • Document metadata      │
                     │  • Vector embeddings       │
                     │  • Audit logs (Q&A pairs)  │
                     │  • Golden Q&A set          │
                     └──────────────────────────┘
```

**Why this stack?**
- **React** — modern, responsive SPA with a polished fintech-inspired UI
- **Django** — batteries-included admin, auth, ORM, and audit logging for the enterprise management layer
- **Flask** — minimal and focused for a narrow, fast RAG API with three endpoints

## Tech Stack

- **React 19** + React Router + Vite — frontend SPA
- **Django 5** — REST API, document management, admin, audit logging
- **Flask** — RAG microservice (ingest, query, eval)
- **PostgreSQL + pgvector** — relational data + vector similarity search
- **OpenAI API** — embeddings (`text-embedding-3-small`) and generation (`gpt-4o-mini`)
- **PyMuPDF** — PDF text extraction
- **Nginx** — frontend static serving + API reverse proxy
- **Docker Compose** — full stack orchestration (4 services)

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

This starts all 4 services:
- **PostgreSQL** (pgvector) on port 5432
- **Flask RAG** on port 5001
- **Django API** on port 8000
- **React frontend** on port 3001

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
# Generate sample insurance PDFs
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

- **React UI**: http://localhost:3001 — login, upload documents, ask questions, view audit logs
- **Django Admin**: http://localhost:8000/admin/ — manage documents and review audit trail
- **Flask API**: http://localhost:5001 — direct RAG API access

## React Frontend

Modern fintech-inspired UI with:
- **Dashboard** — document stats, RAG service health, recent activity feed
- **Query page** — ask questions with real-time answers, cited sources with similarity scores
- **Upload** — drag-and-drop PDF upload with automatic indexing
- **Documents** — browse all indexed policies with status tracking
- **Audit Log** — full governance trail with question/answer pairs, source counts, and model info

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

## Django REST API

All endpoints return JSON. Auth is session-based.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login/` | Authenticate and start session |
| POST | `/api/logout/` | End session |
| GET | `/api/me/` | Current user info |
| GET | `/api/stats/` | Dashboard stats + RAG health |
| GET | `/api/documents/` | List all documents |
| GET | `/api/documents/<id>/` | Document detail + activity |
| POST | `/api/documents/upload/` | Upload and ingest a PDF |
| POST | `/api/query/` | Query indexed documents |
| GET | `/api/audit/` | Audit log entries (with Q&A) |

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

## AI Governance

- **Audit logging** — every document upload, ingestion, query, and login is logged with timestamp, user, IP address
- **Query/answer capture** — full question and generated answer stored in audit trail for compliance review
- **Source tracking** — number of sources and model used recorded per query
- **Admin panel** — read-only audit log in Django admin (no edit/delete permissions)

## Project Structure

```
insurance-rag/
├── frontend/                  # React SPA (Vite)
│   ├── src/
│   │   ├── App.jsx            # Routes and auth context
│   │   ├── App.css            # Afficiency-inspired theme
│   │   ├── api.js             # API client
│   │   ├── components/
│   │   │   └── Layout.jsx     # Sidebar + content layout
│   │   └── pages/
│   │       ├── Login.jsx
│   │       ├── Dashboard.jsx
│   │       ├── Upload.jsx
│   │       ├── Query.jsx
│   │       ├── Documents.jsx
│   │       ├── DocumentDetail.jsx
│   │       └── AuditLog.jsx
│   ├── nginx.conf             # Reverse proxy config
│   └── Dockerfile
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
│   └── Dockerfile
├── django_app/                # Enterprise management layer
│   ├── insurance_project/     # Django project settings
│   ├── documents/             # Main app
│   │   ├── models.py          # PolicyDocument, AuditLog
│   │   ├── api.py             # REST API views
│   │   ├── admin.py           # Admin panel config
│   │   ├── rag_client.py      # HTTP client for Flask service
│   │   └── views.py           # Template views (legacy)
│   └── Dockerfile
├── sample_data/               # Sample insurance PDFs + golden set
│   ├── generate_sample_pdfs.py
│   └── golden_set.json
├── docker-compose.yml
└── .env.example
```
