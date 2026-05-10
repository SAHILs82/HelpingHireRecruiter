import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.cv_score import CVScore
from app.db.models.candidate_application import CandidateApplication
from app.db.models.candidate_details import Candidate
from app.db.models.job_description import JobDescription
from app.db.session import get_session
from app.schemas.cv_scoring_schema import CVScoreResponse
from app.ai.agents.cv_scoring_agent import evaluate_candidate

router = APIRouter()


@router.post("/{application_id}/evaluate", status_code=status.HTTP_201_CREATED)
async def trigger_scoring(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Trigger CV scoring for a specific application.
    Fetches candidate + JD, runs the LLM evaluation, and stores the result.
    """
    # Verify application exists
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        result = await run_in_threadpool(evaluate_candidate, str(application_id))

        if result.get("status") == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Scoring failed: {result.get('error', 'Unknown error')}",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV Scoring pipeline failed: {str(e)}",
        )


@router.get("/application/{application_id}", response_model=List[CVScoreResponse])
async def get_scores_by_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get all scoring results for a specific application.
    Returns all versions if re-scored.
    """
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db.execute(
        select(CVScore)
        .filter(
            CVScore.candidate_id == application.candidate_id,
            CVScore.job_id == application.job_id,
        )
        .order_by(CVScore.version.desc())
    )
    scores = result.scalars().all()

    if not scores:
        raise HTTPException(status_code=404, detail="No scores found for this application")

    return scores


@router.get("/candidate/{candidate_id}", response_model=List[CVScoreResponse])
async def get_scores_by_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get all scores for a specific candidate across all jobs they applied to.
    """
    result = await db.execute(
        select(CVScore)
        .filter(CVScore.candidate_id == candidate_id)
        .order_by(CVScore.created_at.desc())
    )
    return result.scalars().all()

def _normalize_score(raw: float) -> float:
    """If the LLM returned a 0-1 decimal, scale it to 0-100."""
    return round(raw * 100, 1) if raw <= 1.0 else round(raw, 1)


def _score_to_recommendation(raw_score: float) -> str:
    """Derive a recommendation label from the normalized 0-100 score."""
    if raw_score >= 80:
        return "Strong Hire"
    elif raw_score >= 60:
        return "Hire"
    elif raw_score >= 40:
        return "Maybe"
    return "No Hire"


@router.get("/job/{job_id}/leaderboard")
async def get_leaderboard(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get the top scores for a specific job, including candidate names and application IDs.
    """
    result = await db.execute(
        select(CVScore, Candidate.full_name, CandidateApplication.id.label("app_id"))
        .join(Candidate, CVScore.candidate_id == Candidate.id)
        .join(
            CandidateApplication,
            (CandidateApplication.candidate_id == CVScore.candidate_id)
            & (CandidateApplication.job_id == CVScore.job_id),
        )
        .filter(CVScore.job_id == job_id)
        .order_by(CVScore.raw_score.desc())
    )
    
    rows = result.all()
    return [
        {
            "id": str(score.id),
            "application_id": str(app_id),
            "candidate_id": str(score.candidate_id),
            "candidate_name": full_name,
            "score": _normalize_score(score.raw_score),
            "recommendation": _score_to_recommendation(_normalize_score(score.raw_score)),
            "status": score.status,
            "version": score.version,
            "created_at": score.created_at.isoformat()
        }
        for score, full_name, app_id in rows
    ]

@router.get("/job/{job_id}", response_model=List[CVScoreResponse])
async def get_scores_by_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get all scores for a specific job.
    """
    result = await db.execute(
        select(CVScore)
        .filter(CVScore.job_id == job_id)
        .order_by(CVScore.raw_score.desc())
    )
    return result.scalars().all()


@router.patch("/{score_id}")
async def update_score_status(
    score_id: uuid.UUID,
    new_status: str,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Update the status of a score (e.g., from 'scored' to 'reviewed' or 'rescored').
    """
    valid_statuses = {"scored", "rescored", "reviewed", "failed"}
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    score = await db.get(CVScore, score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    score.status = new_status
    await db.commit()
    await db.refresh(score)

    return {"id": str(score.id), "status": score.status}


@router.get("/application/{application_id}/score-detail")
async def get_application_score_detail(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get a rich score detail view for the ScoreDetailPage frontend.
    Looks up the latest CVScore via CandidateApplication and returns
    a shaped payload the UI expects.
    """
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db.execute(
        select(CVScore, Candidate.full_name, JobDescription.role_title)
        .join(Candidate, CVScore.candidate_id == Candidate.id)
        .join(JobDescription, CVScore.job_id == JobDescription.id)
        .filter(
            CVScore.candidate_id == application.candidate_id,
            CVScore.job_id == application.job_id,
        )
        .order_by(CVScore.version.desc())
        .limit(1)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="No scores found for this application")

    score_obj, candidate_name, job_title = row

    # Normalize: if raw_score looks like a 0-1 decimal, scale to 0-100
    raw = score_obj.raw_score
    normalized_score = _normalize_score(raw)

    # Normalize category breakdowns too
    raw_breakdown = score_obj.category_scores or {}
    breakdown = {k: _normalize_score(v) for k, v in raw_breakdown.items()} if raw_breakdown else {}

    return {
        "application_id": str(application_id),
        "score_id": str(score_obj.id),
        "candidate_name": candidate_name or "Unknown",
        "job_title": job_title or "Unknown Role",
        "score": normalized_score,
        "breakdown": breakdown,
        "strengths": score_obj.strengths or [],
        "weaknesses": score_obj.weaknesses or [],
        "missing_requirements": [],  # Could be derived from weaknesses
        "recommendation": _score_to_recommendation(normalized_score),
        "agent_summary": score_obj.reasoning_summary or "No summary available.",
        "status": score_obj.status,
        "created_at": score_obj.created_at.isoformat(),
    }
