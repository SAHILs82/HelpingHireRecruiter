import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_session
from app.db.models.skill_gap_report import SkillGapReportRecord
from app.db.models.candidate_application import CandidateApplication
from app.schemas.skill_gap import SkillGapReportResponse, SkillGapReportUpdate
from app.ai.agents.skill_gap_agent import analyze_skill_gap

router = APIRouter()

@router.post("/{application_id}", status_code=status.HTTP_201_CREATED)
async def trigger_skill_gap_analysis(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Trigger Skill Gap analysis for a specific application.
    Fetches the candidate and JD data, runs the LLM tool-calling agent, and stores the result.
    """
    # Verify application exists
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        result = await run_in_threadpool(analyze_skill_gap, str(application_id))

        if result.get("status") == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill Gap pipeline failed: {str(e)}",
        )


@router.get("/{application_id}", response_model=SkillGapReportResponse)
async def get_skill_gap_report(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get the skill gap report for a specific application.
    """
    result = await db.execute(
        select(SkillGapReportRecord)
        .filter(SkillGapReportRecord.application_id == application_id)
    )
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="No skill gap report found for this application")

    return report


@router.patch("/{report_id}", response_model=SkillGapReportResponse)
async def update_skill_gap_report(
    report_id: uuid.UUID,
    update_data: SkillGapReportUpdate,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Manually update a skill gap report (e.g., recruiter overrides a gap).
    """
    report = await db.get(SkillGapReportRecord, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Skill gap report not found")

    if update_data.gaps is not None:
        report.gaps = [gap.model_dump() for gap in update_data.gaps]
    if update_data.impact_score is not None:
        report.impact_score = update_data.impact_score
    if update_data.summary is not None:
        report.summary = update_data.summary

    await db.commit()
    await db.refresh(report)

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill_gap_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
) -> None:
    """
    Delete a skill gap report.
    """
    report = await db.get(SkillGapReportRecord, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Skill gap report not found")

    await db.delete(report)
    await db.commit()
