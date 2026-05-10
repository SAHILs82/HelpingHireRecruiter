import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.db.models.candidate_application import CandidateApplication
from app.db.models.candidate_details import Candidate
from app.db.models.job_description import JobDescription
from app.db.session import get_session
from app.schemas.candidate_application import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter()

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Link a candidate to a job (create an application).
    """
    # Verify candidate exists
    candidate = await db.get(Candidate, payload.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Verify job exists
    job = await db.get(JobDescription, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    application = CandidateApplication(**payload.model_dump())
    db.add(application)
    
    try:
        await db.commit()
        await db.refresh(application)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already exists for this candidate and job."
        )

    return application


@router.get("/job/{job_id}")
async def get_applications_by_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get all applications for a specific job (HR view) with candidate details.
    """
    result = await db.execute(
        select(CandidateApplication, Candidate.full_name, Candidate.email)
        .join(Candidate, CandidateApplication.candidate_id == Candidate.id)
        .filter(CandidateApplication.job_id == job_id)
    )
    
    rows = result.all()
    return [
        {
            "id": str(app.id),
            "candidate_id": str(app.candidate_id),
            "job_id": str(app.job_id),
            "status": app.status,
            "applied_at": app.applied_at.isoformat(),
            "candidate_name": full_name,
            "candidate_email": email
        }
        for app, full_name, email in rows
    ]


@router.get("/candidate/{candidate_id}", response_model=List[ApplicationResponse])
async def get_applications_by_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Get all jobs a specific candidate applied to (Candidate view).
    """
    result = await db.execute(
        select(CandidateApplication).filter(CandidateApplication.candidate_id == candidate_id)
    )
    return result.scalars().all()


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Update application status.
    """
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)
        
    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_200_OK)
async def delete_application(
    application_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Remove a candidate-job link.
    """
    application = await db.get(CandidateApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    await db.delete(application)
    await db.commit()
    return {"status": "deleted", "id": str(application_id)}
