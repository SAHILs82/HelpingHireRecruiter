import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.jd_intake import JDIntake
from app.db.session import get_session
from app.schemas.jd_intake import JDIntakeCreate, JDIntakeUpdate, JDIntakeResponse
from app.agents.jd_generator_agent import generate_job_description

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_jd_intake(
    payload: JDIntakeCreate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Save a new intake form submission as a draft in the database.
    Validated by the JDIntakeCreate Pydantic schema.
    """
    intake = JDIntake(**payload.model_dump())
    db.add(intake)
    await db.commit()
    await db.refresh(intake)
    return {"id": str(intake.id), "status": "saved"}


@router.get("/{intake_id}", response_model=JDIntakeResponse)
async def get_jd_intake(
    intake_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Retrieve an existing intake form from the database.
    """
    result = await db.execute(select(JDIntake).filter(JDIntake.id == intake_id))
    intake = result.scalars().first()
    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JD Intake not found"
        )
    return intake


@router.patch("/{intake_id}")
async def update_jd_intake(
    intake_id: uuid.UUID,
    payload: JDIntakeUpdate,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Update an existing intake form draft in the database.
    Only fields provided (non-None) will be updated.
    """
    result = await db.execute(select(JDIntake).filter(JDIntake.id == intake_id))
    intake = result.scalars().first()
    
    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JD Intake not found"
        )
        
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(intake, field, value)
        
    await db.commit()
    await db.refresh(intake)
    return {"id": str(intake.id), "status": "updated"}


@router.post("/{intake_id}/generate", status_code=status.HTTP_200_OK)
async def trigger_jd_generation(
    intake_id: uuid.UUID,
    db: AsyncSession = Depends(get_session)
) -> Any:
    """
    Test the AI Agent pipeline!
    Fetches the intake from the DB, generates a job description with LangChain, 
    and stores the new Job Description back into the DB linked to this intake.
    """
    # 1. Ensure intake exists (just a quick check before heavy lifting)
    result = await db.execute(select(JDIntake).filter(JDIntake.id == intake_id))
    intake = result.scalars().first()
    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JD Intake not found"
        )

    # 2. Trigger the TRUE agentic flow
    from app.agents.jd_generator_agent import generate_job_description
    from app.services.ai.jd_generator_service import fetch_intake_from_db, store_generated_jd
    
    try:
        # Step A: Fetch the intake object from DB formatted specifically for the AI agent
        agent_intake = await run_in_threadpool(fetch_intake_from_db, str(intake_id))
        
        # Step B: Securely pass the object into the agent (Fixes 'str' attribute Error)
        # The agent returns a strictly-typed JDGeneratorResponse
        response_model = await run_in_threadpool(generate_job_description, agent_intake)
        
        # Step C: Ask the service layer to store the final generated output payload into the DB
        new_jd_id = await run_in_threadpool(store_generated_jd, str(intake_id), response_model)
        
        return {
            "status": "success",
            "message": "Agent completed the full pipeline (Fetch -> Generate -> Store).",
            "jd_intake_id": str(intake_id),
            "agent_summary": f"Successfully validated Pydantic output and saved JD with ID {new_jd_id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent pipeline failed: {str(e)}"
        )
