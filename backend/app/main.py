from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI

from app.api.schemas import ScreeningRequest
from app.core.config import settings
from app.models.schemas import CandidateProfile
from app.services.graph_runner import run_hiring_graph
from app.utils.logging import request_logging_middleware
from app.utils.tracing import setup_langsmith_tracing

app = FastAPI(title=settings.app_name)
app.middleware("http")(request_logging_middleware)
app.state.langsmith_enabled = setup_langsmith_tracing()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "langsmith_tracing": "enabled" if app.state.langsmith_enabled else "disabled",
    }


@app.post("/screen")
async def screen_candidates(payload: ScreeningRequest) -> Dict[str, Any]:
    candidates: List[CandidateProfile] = [
        CandidateProfile(
            candidate_id=item.candidate_id,
            name=item.name,
            email=item.email,
            cv_text=item.cv_text,
            total_experience_years=item.total_experience_years,
            declared_skills=item.declared_skills,
        )
        for item in payload.candidates
    ]
    dossiers = await run_hiring_graph(
        job_id=payload.job_id,
        jd_text=payload.jd_text,
        candidates=candidates,
    )

    response = []
    for candidate_id, dossier in dossiers.items():
        questions = getattr(dossier, "_interview_questions", [])
        response.append(
            {
                "candidate_id": candidate_id,
                "score": dossier.score.model_dump(),
                "skill_gap": dossier.skill_gap.model_dump(),
                "decision": dossier.final_decision.model_dump() if dossier.final_decision else None,
                "interview_questions": [q.model_dump() for q in questions],
            }
        )
    return {"job_id": payload.job_id, "results": response}
