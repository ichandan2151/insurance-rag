"""Tests for Flask API endpoints."""
import json
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "insurance-rag"


class TestIngestEndpoint:
    def test_ingest_no_file(self, client):
        resp = client.post("/ingest")
        assert resp.status_code == 400
        assert "No file provided" in resp.get_json()["error"]

    def test_ingest_non_pdf(self, client):
        from io import BytesIO

        data = {"file": (BytesIO(b"not a pdf"), "test.txt")}
        resp = client.post("/ingest", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert "PDF" in resp.get_json()["error"]


class TestQueryEndpoint:
    def test_query_no_body(self, client):
        resp = client.post("/query", content_type="application/json")
        assert resp.status_code == 400

    def test_query_no_question(self, client):
        resp = client.post("/query", json={})
        assert resp.status_code == 400
        assert "question" in resp.get_json()["error"]

    @patch("app.retrieve")
    def test_query_no_results(self, mock_retrieve, client):
        mock_retrieve.return_value = []
        resp = client.post("/query", json={"question": "What is covered?"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "No relevant documents" in data["answer"]

    @patch("app.generate_answer")
    @patch("app.retrieve")
    def test_query_with_results(self, mock_retrieve, mock_generate, client):
        mock_retrieve.return_value = [
            {
                "chunk_id": 1,
                "content": "Coverage A is $350,000.",
                "page_number": 1,
                "chunk_index": 0,
                "document_id": 1,
                "filename": "policy.pdf",
                "title": "Homeowners Policy",
                "similarity": 0.92,
            }
        ]
        mock_generate.return_value = {
            "answer": "Coverage A is $350,000. [Source: policy.pdf, Page 1]",
            "sources": [{"filename": "policy.pdf", "page_number": 1, "similarity": 0.92}],
            "model": "gpt-4o-mini",
        }

        resp = client.post("/query", json={"question": "What is dwelling coverage?"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "answer" in data
        assert "sources" in data


class TestEvalEndpoint:
    def test_eval_empty_golden_set(self, client):
        resp = client.post("/eval", json={"golden_set": []})
        assert resp.status_code == 400

    @patch("app.generate_answer")
    @patch("app.retrieve")
    def test_eval_with_inline_golden_set(self, mock_retrieve, mock_generate, client):
        mock_retrieve.return_value = [
            {
                "chunk_id": 1,
                "content": "The deductible is $1,000.",
                "page_number": 1,
                "chunk_index": 0,
                "document_id": 1,
                "filename": "policy.pdf",
                "title": "Policy",
                "similarity": 0.85,
            }
        ]
        mock_generate.return_value = {
            "answer": "The deductible is $1,000 per occurrence.",
            "sources": [{"filename": "policy.pdf", "page_number": 1, "similarity": 0.85}],
            "model": "gpt-4o-mini",
        }

        golden = [
            {
                "question": "What is the deductible?",
                "expected_answer": "The deductible is $1,000 per occurrence.",
            }
        ]
        resp = client.post("/eval", json={"golden_set": golden})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "summary" in data
        assert "results" in data
        assert data["summary"]["total_questions"] == 1
        assert len(data["results"]) == 1
