import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    """Schema for linking a candidate to a job."""
    candidate_id: uuid.UUID
    job_id: uuid.UUID


class ApplicationUpdate(BaseModel):
    """Schema for updating an application (e.g. status)."""
    status: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Schema for application response."""
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    applied_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
