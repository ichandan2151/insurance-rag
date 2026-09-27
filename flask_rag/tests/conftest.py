"""Shared fixtures for Flask RAG tests."""
import os
import sys
import pytest

# Ensure flask_rag package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app as flask_app


@pytest.fixture
def client():
    """Flask test client."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c
