import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.candidate_details import Candidate
from app.db.models.job_description import JobDescription
from app.db.models.candidate_application import CandidateApplication
from app.db.session import get_session
from app.schemas.candidate_details import CandidateUpdate
from app.services.cv_parser import extract_text
from app.ai.agents.cv_parser_agent import parse_and_store_cv
router = APIRouter()

@router.post("/upload-cv", status_code=status.HTTP_201_CREATED)
async def upload_candidate_cv(
    job_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Upload a candidate's resume (PDF), extract text, parse with LLM, and save to DB.
    Also automatically links the candidate to the specified job.
    """
    allowed_extensions = {".pdf"}
    file_ext = "." + file.filename.lower().split('.')[-1]
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Only PDF files are supported currently."
        )

    try:
        # Verify job exists before doing heavy work
        job = await db.get(JobDescription, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job description not found")

        # 1. Read file bytes
        file_bytes = await file.read()
        
        # 2. Extract raw text from File (Cpu intensive, run in threadpool)
        cv_text = await run_in_threadpool(extract_text, file_bytes, file.filename)
        
        if not cv_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from the file. Ensure it is not encrypted or an image-only scan."
            )

        # 3. Use LLM Agent to parse text and store to DB
        candidate_id = str(uuid.uuid4())
        result = await run_in_threadpool(parse_and_store_cv, cv_text, candidate_id)
        
        # 4. Create application link
        if result.get("status") != "failed":
            application = CandidateApplication(
                candidate_id=uuid.UUID(candidate_id),
                job_id=job_id
            )
            db.add(application)
            await db.commit()
            
            result["application_id"] = str(application.id)
            result["job_id"] = str(job_id)
        
        return result

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV Upload & Parsing Failed: {str(e)}"
        )


@router.patch("/{candidate_id}")
async def update_candidate(
    candidate_id: uuid.UUID,
    payload: CandidateUpdate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Update an existing candidate profile.
    Only fields provided (non-None) will be updated.
    """
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
        
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
        
    await db.commit()
    await db.refresh(candidate)
    return {"id": str(candidate.id), "status": "updated"}


@router.delete("/{candidate_id}", status_code=status.HTTP_200_OK)
async def delete_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Delete an existing candidate profile from the database.
    """
    candidate = await db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
        
    await db.delete(candidate)
    await db.commit()
    return {"status": "deleted", "id": str(candidate_id)}
