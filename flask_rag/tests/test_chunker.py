"""Tests for the chunking service."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.chunker import chunk_text, _split_into_sentences, ChunkResult


class TestSplitIntoSentences:
    def test_basic_sentences(self):
        text = "First sentence. Second sentence. Third one!"
        result = _split_into_sentences(text)
        assert result == ["First sentence.", "Second sentence.", "Third one!"]

    def test_empty_string(self):
        assert _split_into_sentences("") == []

    def test_single_sentence(self):
        result = _split_into_sentences("Just one sentence.")
        assert result == ["Just one sentence."]

    def test_question_marks(self):
        result = _split_into_sentences("What is covered? Everything listed.")
        assert result == ["What is covered?", "Everything listed."]


class TestChunkText:
    def test_single_page_small_text(self):
        pages = [{"page_number": 1, "text": "Short text."}]
        chunks = chunk_text(pages, chunk_size=512, chunk_overlap=64)
        assert len(chunks) == 1
        assert chunks[0].content == "Short text."
        assert chunks[0].page_number == 1
        assert chunks[0].chunk_index == 0

    def test_multiple_pages(self):
        pages = [
            {"page_number": 1, "text": "Page one content."},
            {"page_number": 2, "text": "Page two content."},
        ]
        chunks = chunk_text(pages, chunk_size=512, chunk_overlap=64)
        assert len(chunks) == 2
        assert chunks[0].page_number == 1
        assert chunks[1].page_number == 2

    def test_large_text_splits_into_chunks(self):
        long_text = ". ".join([f"Sentence number {i}" for i in range(100)]) + "."
        pages = [{"page_number": 1, "text": long_text}]
        chunks = chunk_text(pages, chunk_size=100, chunk_overlap=10)
        assert len(chunks) > 1
        # All chunks should reference page 1
        assert all(c.page_number == 1 for c in chunks)
        # Chunk indices should be sequential
        for i, c in enumerate(chunks):
            assert c.chunk_index == i

    def test_chunk_result_type(self):
        pages = [{"page_number": 3, "text": "Test content here."}]
        chunks = chunk_text(pages, chunk_size=512, chunk_overlap=64)
        assert isinstance(chunks[0], ChunkResult)

    def test_empty_pages(self):
        chunks = chunk_text([], chunk_size=512, chunk_overlap=64)
        assert chunks == []
