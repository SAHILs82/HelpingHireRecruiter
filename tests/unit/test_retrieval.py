from app.retrieval.chunking import section_aware_chunk_cv
from app.services.evidence_service import retrieve_candidate_evidence


def test_section_aware_chunking() -> None:
    text = "Experience\nBuilt FastAPI service\nSkills\nPython LangChain RAG"
    chunks = section_aware_chunk_cv(text, candidate_id="c1")
    assert chunks
    assert any(chunk.section in {"experience", "skills"} for chunk in chunks)


def test_retrieve_candidate_evidence() -> None:
    text = "Experience\nBuilt FastAPI and RAG chatbot\nSkills\nPython LangChain"
    evidence = retrieve_candidate_evidence("c1", text, "Python FastAPI LangChain")
    assert len(evidence) > 0
