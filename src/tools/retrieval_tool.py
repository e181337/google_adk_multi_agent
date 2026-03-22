from typing import Any
from google.adk.tools import tool

from src.data.knowledge_base import KNOWLEDGE_BASE, KnowledgeBaseChunk


def _normalize_text(text: str) -> str:
    if text is None:
        return ""
    return " ".join(text.lower().strip().split())


def _score_chunk(tokens: list[str], chunk: KnowledgeBaseChunk) -> int:
    searchable_text = _normalize_text(
        f"{chunk.title} {chunk.content} {' '.join(chunk.tags)} {chunk.category}"
    )

    score = 0
    for token in tokens:
        if token in searchable_text:
            score += 1

    return score


@tool
def retrieval_tool(query_text: str, max_results: int = 3) -> list[dict[str, Any]]:
    if not query_text or not query_text.strip():
        raise ValueError("query_text cannot be empty")

    if not isinstance(max_results, int):
        raise ValueError("max_results must be an int")

    if max_results <= 0:
        raise ValueError("max_results must be positive")

    normalized_query = _normalize_text(query_text)
    tokens = normalized_query.split()

    scored_chunks: list[dict[str, Any]] = []

    for chunk in KNOWLEDGE_BASE:
        score = _score_chunk(tokens, chunk)

        if score > 0:
            scored_chunks.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "content": chunk.content,
                    "category": chunk.category,
                    "tags": chunk.tags,
                    "score": score,
                }
            )

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    return scored_chunks[:max_results]
