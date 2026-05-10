import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.job_description import JobDescription
from app.db.session import get_session

router = APIRouter()


@router.get("/")
async def list_job_descriptions(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    List all generated job descriptions, newest first.
    """
    result = await db.execute(
        select(JobDescription).order_by(JobDescription.created_at.desc()).limit(limit).offset(offset)
    )
    jobs = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "role_title": j.role_title,
            "level": j.level,
            "company_name": j.company_name,
            "location": j.location,
            "employment_type": j.employment_type,
            "status": j.status,
            "jd_intake_id": str(j.jd_intake_id) if j.jd_intake_id else None,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@router.get("/{job_id}")
async def get_job_description(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get a single job description with full details including structured_output.
    """
    job = await db.get(JobDescription, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    return {
        "id": str(job.id),
        "role_title": job.role_title,
        "level": job.level,
        "jd_text": job.jd_text,
        "structured_output": job.structured_output,
        "status": job.status,
        "experience_level": job.experience_level,
        "company_name": job.company_name,
        "location": job.location,
        "employment_type": job.employment_type,
        "salary_range": job.salary_range,
        "source": job.source,
        "confidence_score": job.confidence_score,
        "jd_intake_id": str(job.jd_intake_id) if job.jd_intake_id else None,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }
