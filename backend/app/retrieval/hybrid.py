from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.retrieval.chunking import CVChunk


@dataclass
class RetrievedPassage:
    chunk: CVChunk
    bm25_score: float
    vector_score: float
    hybrid_score: float


class HybridRetriever:
    """
    Lightweight hybrid retriever scaffold.
    Uses lexical overlap as BM25 proxy and a simple semantic proxy score.
    Replace score methods with real BM25/vector implementations in production.
    """

    def __init__(self, alpha: float = 0.5) -> None:
        self.alpha = alpha

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token.strip().lower() for token in text.split() if token.strip()}

    def bm25_proxy(self, query: str, text: str) -> float:
        q = self._tokenize(query)
        t = self._tokenize(text)
        if not q:
            return 0.0
        return len(q.intersection(t)) / len(q)

    def vector_proxy(self, query: str, text: str) -> float:
        # Placeholder semantic score. Hook dense embedding similarity here.
        q = query.lower()
        hit = 0.0
        for phrase in ["built", "designed", "deployed", "led", "optimized"]:
            if phrase in text.lower() and phrase in q:
                hit += 0.2
        return min(1.0, hit)

    def retrieve(self, query: str, chunks: List[CVChunk], top_k: int = 8) -> List[RetrievedPassage]:
        scored: List[RetrievedPassage] = []
        for chunk in chunks:
            bm25 = self.bm25_proxy(query, chunk.text)
            vec = self.vector_proxy(query, chunk.text)
            hybrid = self.alpha * vec + (1 - self.alpha) * bm25
            scored.append(RetrievedPassage(chunk, bm25, vec, hybrid))
        scored.sort(key=lambda x: x.hybrid_score, reverse=True)
        return scored[:top_k]
