import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.review_flow import EvidenceSpan

class CategoryScores(BaseModel):
    """Per-category breakdown aligned with JDRubric.weighting."""
    skills: float = 0.0
    experience: float = 0.0
    projects: float = 0.0
    education: float = 0.0

class CVScoreBase(BaseModel):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    raw_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    evidence: List[EvidenceSpan] = Field(default_factory=list)
    reasoning_summary: str
    category_scores: Optional[CategoryScores] = None
    status: str = "scored"
    version: int = 1
    scored_by: Optional[str] = None
    scoring_model: Optional[str] = None

class CVScoreCreate(BaseModel):
    """Input to trigger scoring."""
    job_id: uuid.UUID
    candidate_id: uuid.UUID

class CVScoreResponse(CVScoreBase):
    """Full score result returned from API."""
    id: uuid.UUID
    scored_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
