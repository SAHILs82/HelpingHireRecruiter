import pytest

from app.models.schemas import CandidateProfile
from app.services.graph_runner import run_hiring_graph


@pytest.mark.asyncio
async def test_run_hiring_graph_returns_decisions() -> None:
    candidates = [
        CandidateProfile(
            candidate_id="c1",
            name="A",
            cv_text="Experience\nBuilt FastAPI and LangChain apps\nSkills\nPython RAG",
        )
    ]
    result = await run_hiring_graph("job-1", "Need Python FastAPI LangChain RAG", candidates)
    assert "c1" in result
    assert result["c1"].final_decision is not None
