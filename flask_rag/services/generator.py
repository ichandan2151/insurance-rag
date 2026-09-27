"""Answer generation service with citations."""
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an insurance policy expert assistant. Answer questions based ONLY on the provided context passages.

Rules:
1. Only use information from the provided context passages.
2. Cite your sources using [Source: filename, Page X] format after each claim.
3. If the context doesn't contain enough information to answer, say so explicitly.
4. Be precise and specific — insurance policy details matter.
5. Do not make up or infer policy details not present in the context."""

USER_PROMPT_TEMPLATE = """Context passages:
{context}

Question: {question}

Provide a detailed answer with citations."""


def generate_answer(query: str, retrieved_chunks: list[dict]) -> dict:
    """Generate an answer from retrieved chunks with citations."""
    # Format context with source markers
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_label = f"[Passage {i} — {chunk['title']}, Page {chunk['page_number']}]"
        context_parts.append(f"{source_label}\n{chunk['content']}")

    context = "\n\n".join(context_parts)

    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                context=context, question=query
            )},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    answer_text = response.choices[0].message.content

    return {
        "answer": answer_text,
        "sources": [
            {
                "filename": c["filename"],
                "title": c["title"],
                "page_number": c["page_number"],
                "similarity": c["similarity"],
                "excerpt": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"],
            }
            for c in retrieved_chunks
        ],
        "model": Config.LLM_MODEL,
    }
