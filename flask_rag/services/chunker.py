"""PDF text extraction and chunking service."""
import fitz  # PyMuPDF
from dataclasses import dataclass
from config import Config


@dataclass
class ChunkResult:
    content: str
    page_number: int
    chunk_index: int


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from each page of a PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages.append({"page_number": page_num + 1, "text": text.strip()})
    doc.close()
    return pages


def chunk_text(
    pages: list[dict],
    chunk_size: int = Config.CHUNK_SIZE,
    chunk_overlap: int = Config.CHUNK_OVERLAP,
) -> list[ChunkResult]:
    """Split extracted pages into overlapping chunks.

    Pages shorter than chunk_size are kept as a single chunk to preserve
    structured content like declarations pages and coverage summaries.
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        # Keep short pages intact — declarations pages, summaries, etc.
        if len(text) <= chunk_size * 1.5:
            chunks.append(ChunkResult(
                content=text.strip(),
                page_number=page_number,
                chunk_index=chunk_index,
            ))
            chunk_index += 1
            continue

        # Split longer pages by sentences with overlap
        sentences = _split_into_sentences(text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(ChunkResult(
                    content=current_chunk.strip(),
                    page_number=page_number,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1

                # Keep overlap from end of current chunk
                words = current_chunk.split()
                overlap_words = words[-chunk_overlap:] if len(words) > chunk_overlap else words
                current_chunk = " ".join(overlap_words) + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Don't forget the last chunk from this page
        if current_chunk.strip():
            chunks.append(ChunkResult(
                content=current_chunk.strip(),
                page_number=page_number,
                chunk_index=chunk_index,
            ))
            chunk_index += 1

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """Basic sentence splitter."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]
