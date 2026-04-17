from __future__ import annotations

from typing import List

from app.retrieval.hybrid import RetrievedPassage


class PassageReranker:
    """
    Reranker shim. Replace with cross-encoder model call in production.
    """

    def rerank(self, query: str, passages: List[RetrievedPassage], top_k: int = 5) -> List[RetrievedPassage]:
        query_tokens = set(query.lower().split())

        def score(p: RetrievedPassage) -> float:
            text_tokens = set(p.chunk.text.lower().split())
            overlap = len(query_tokens.intersection(text_tokens))
            return p.hybrid_score + (overlap * 0.01)

        reranked = sorted(passages, key=score, reverse=True)
        return reranked[:top_k]
