"""Client for communicating with the Flask RAG microservice."""
import requests
from django.conf import settings


class RAGServiceError(Exception):
    pass


def _url(path: str) -> str:
    return f"{settings.RAG_SERVICE_URL}{path}"


def health_check() -> dict:
    resp = requests.get(_url("/health"), timeout=5)
    resp.raise_for_status()
    return resp.json()


def ingest_document(file_obj, title: str) -> dict:
    """Send a PDF to the Flask RAG /ingest endpoint."""
    resp = requests.post(
        _url("/ingest"),
        files={"file": (file_obj.name, file_obj.read(), "application/pdf")},
        data={"title": title},
        timeout=120,
    )
    if resp.status_code != 201:
        error = resp.json().get("error", "Unknown error")
        raise RAGServiceError(f"Ingest failed: {error}")
    return resp.json()


def query(question: str, top_k: int = 5) -> dict:
    """Send a question to the Flask RAG /query endpoint."""
    resp = requests.post(
        _url("/query"),
        json={"question": question, "top_k": top_k},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def run_eval(top_k: int = 5) -> dict:
    """Trigger the Flask RAG /eval endpoint."""
    resp = requests.post(
        _url("/eval"),
        json={"top_k": top_k},
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()
