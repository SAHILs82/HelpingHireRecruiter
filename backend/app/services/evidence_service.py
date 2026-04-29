from __future__ import annotations

from typing import List

from app.schemas import EvidenceSpan
from app.retrieval.chunking import expand_query_terms, section_aware_chunk_cv
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import PassageReranker


def retrieve_candidate_evidence(candidate_id: str, cv_text: str, query: str) -> List[EvidenceSpan]:
    chunks = section_aware_chunk_cv(cv_text=cv_text, candidate_id=candidate_id)
    retriever = HybridRetriever(alpha=0.55)
    reranker = PassageReranker()

    merged = []
    for expanded in expand_query_terms(query):
        merged.extend(retriever.retrieve(expanded, chunks, top_k=10))

    ranked = reranker.rerank(query, merged, top_k=5)
    return [
        EvidenceSpan(
            source_chunk_id=item.chunk.chunk_id,
            quote=item.chunk.text[:300],
            relevance_score=min(1.0, item.hybrid_score),
        )
        for item in ranked
    ]
