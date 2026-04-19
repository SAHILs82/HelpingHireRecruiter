import uuid
from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class BiasCategory(str, Enum):
    """Types of bias the detector can identify."""
    GENDER = "gender"
    AGE_PROXY = "age_proxy"
    ETHNICITY_PROXY = "ethnicity_proxy"
    EDUCATION_PEDIGREE = "education_pedigree"
    SOCIOECONOMIC = "socioeconomic"
    DISABILITY_PROXY = "disability_proxy"
    NONE = "none"

class BiasFlag(BaseModel):
    """A single bias flag with its evidence."""
    flag: str                           
    category: BiasCategory              
    severity: Literal["low", "medium", "high"] = "low"
    source_quote: Optional[str] = None  

class BiasReportBase(BaseModel):
    """Core bias report data."""
    cv_score_id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    risk_level: Literal["low", "medium", "high"] = "low"
    bias_flags: List[BiasFlag] = Field(default_factory=list)
    bias_categories: List[BiasCategory] = Field(default_factory=list)
    mitigation_actions: List[str] = Field(default_factory=list)
    detection_confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    rationale: str
    reviewed_text: Optional[str] = None
    version: int = 1
    detected_by: Optional[str] = None
    detection_model: Optional[str] = None

class BiasReportCreate(BaseModel):
    """Input to trigger bias detection."""
    cv_score_id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID

class BiasReportResponse(BiasReportBase):
    """Full bias report returned from API."""
    id: uuid.UUID
    detected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
