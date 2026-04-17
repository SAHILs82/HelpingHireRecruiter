from __future__ import annotations

import asyncio
import time

from app.models.schemas import CandidateProfile
from app.services.graph_runner import run_hiring_graph


async def main() -> None:
    candidates = [
        CandidateProfile(
            candidate_id=f"c{i}",
            name=f"Candidate {i}",
            cv_text="Experience\nBuilt Python FastAPI services and LangChain RAG workflows.\nSkills\nPython FastAPI LangChain RAG",
        )
        for i in range(1, 101)
    ]
    start = time.perf_counter()
    await run_hiring_graph("job-benchmark", "Need Python FastAPI LangChain RAG", candidates)
    elapsed = time.perf_counter() - start
    print(f"Processed {len(candidates)} CVs in {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
