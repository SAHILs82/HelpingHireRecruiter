from __future__ import annotations

# 1. SETUP TRACING FIRST (Before any LangChain-dependent imports)
from app.utils.tracing import setup_langsmith_tracing
TRACING_ENABLED = setup_langsmith_tracing()

from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI

from app.api.schemas import ScreeningRequest
from app.core.config import settings
from app.db.session import dispose_async_engine
from app.schemas import CandidateProfile
# from app.services.graph_runner import run_hiring_graph
from app.utils.logging import request_logging_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_async_engine()


from fastapi.middleware.cors import CORSMiddleware
from app.api.jd_intake import router as jd_intake_router
from app.api.cv_parsing import router as cv_parsing_router
from app.api.candidate_application import router as candidate_application_router
from app.api.cv_scoring import router as cv_scoring_router
from app.api.job_description import router as job_description_router

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)
app.state.langsmith_enabled = TRACING_ENABLED

app.include_router(jd_intake_router, prefix="/api/jd/intake", tags=["JD Intake"])
app.include_router(cv_parsing_router, prefix="/api/cv-parsing", tags=["CV Parsing"])
app.include_router(candidate_application_router, prefix="/api/applications", tags=["Candidate Applications"])
app.include_router(cv_scoring_router, prefix="/api/scoring", tags=["CV Scoring"])
app.include_router(job_description_router, prefix="/api/jobs", tags=["Job Descriptions"])

@app.get("/health")
async def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "langsmith_tracing": "enabled" if app.state.langsmith_enabled else "disabled",
    }


@app.post("/screen")
async def screen_candidates(payload: ScreeningRequest) -> Dict[str, Any]:
    return {"message": "Screening graph is currently disabled during refactor."}
#    candidates: List[CandidateProfile] = [
#        CandidateProfile(
#            candidate_id=item.candidate_id,
#            name=item.name,
#            email=item.email,
#            cv_text=item.cv_text,
#            total_experience_years=item.total_experience_years,
#            declared_skills=item.declared_skills,
#        )
#        for item in payload.candidates
#    ]
#    dossiers = await run_hiring_graph(
#        job_id=payload.job_id,
#        jd_text=payload.jd_text,
#        candidates=candidates,
#    )
#
#    response = []
#    for candidate_id, dossier in dossiers.items():
#        questions = getattr(dossier, "_interview_questions", [])
#        response.append(
#            {
#                "candidate_id": candidate_id,
#                "score": dossier.score.model_dump(),
#                "skill_gap": dossier.skill_gap.model_dump(),
#                "decision": dossier.final_decision.model_dump() if dossier.final_decision else None,
#                "interview_questions": [q.model_dump() for q in questions],
#            }
#        )
#    return {"job_id": payload.job_id, "results": response}
