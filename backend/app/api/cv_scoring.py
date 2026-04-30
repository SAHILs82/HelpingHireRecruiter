import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.cv_score import CVScore
from app.db.models.candidate_application import CandidateApplication
from app.db.session import get_session
from app.schemas.cv_score import CVScoreResponse
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


@router.get("/job/{job_id}", response_model=List[CVScoreResponse])
async def get_scores_by_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get all scores for a specific job across all candidates (HR leaderboard view).
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
