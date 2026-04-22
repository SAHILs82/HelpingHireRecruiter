import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.jd_intake import JDIntake
from app.db.session import get_db

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_jd_intake(
    payload: dict,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Save a new basic form intake as a draft in the database.
    (Validated by frontend schema)
    """
    intake = JDIntake(**payload)
    db.add(intake)
    await db.commit()
    await db.refresh(intake)
    return {"id": str(intake.id), "status": "saved"}


@router.get("/{intake_id}")
async def get_jd_intake(
    intake_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
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
    return {
        "id": str(intake.id),
        "company_name": intake.company_name,
        "salary_min": intake.salary_min,
        "salary_max": intake.salary_max,
        "experience_min": intake.experience_min,
        "experience_max": intake.experience_max,
        "domain": intake.domain,
        "role_type": intake.role_type,
        "preferred_education": intake.preferred_education,
        "location": intake.location,
        "description": intake.description
    }


@router.patch("/{intake_id}")
async def update_jd_intake(
    intake_id: uuid.UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update an existing intake form draft in the database.
    Only fields provided in the dictionary will be updated.
    """
    result = await db.execute(select(JDIntake).filter(JDIntake.id == intake_id))
    intake = result.scalars().first()
    
    if not intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JD Intake not found"
        )
        
    for field, value in payload.items():
        if hasattr(intake, field):
            setattr(intake, field, value)
        
    await db.commit()
    await db.refresh(intake)
    return {"id": str(intake.id), "status": "updated"}
