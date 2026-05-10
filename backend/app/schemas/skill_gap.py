import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SkillGapItemSchema(BaseModel):
    skill: str
    gap_type: Literal["missing", "superficial", "outdated", "context_mismatch", "needs_clarification"]
    status: Literal["critical", "trainable", "non_critical"]
    evidence_reasoning: str
    estimated_upskill_weeks: int

class SkillGapReportBase(BaseModel):
    application_id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    gaps: List[SkillGapItemSchema] = Field(default_factory=list)
    impact_score: float = Field(default=0.0)
    summary: Optional[str] = None

class SkillGapReportCreate(BaseModel):
    application_id: uuid.UUID

class SkillGapReportResponse(SkillGapReportBase):
    id: uuid.UUID
    analyzed_by: Optional[str] = None
    analysis_model: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class SkillGapReportUpdate(BaseModel):
    # Allows recruiter to manually override/dismiss gaps
    gaps: Optional[List[SkillGapItemSchema]] = None
    impact_score: Optional[float] = None
    summary: Optional[str] = None
