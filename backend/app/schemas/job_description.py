import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SkillRequirement(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    mandatory: bool = False

class JDRubric(BaseModel):
    role_title: str
    level: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[float] = None
    source: Optional[str] = None
    
    must_have_skills: List[SkillRequirement]
    nice_to_have_skills: List[SkillRequirement] = Field(default_factory=list)
    experience_level: Optional[float] = None  # Aligned with DB model float field
    education_preferences: List[str] = Field(default_factory=list)
    behavioral_signals: List[str] = Field(default_factory=list)
    weighting: Dict[str, float] = Field(
        default_factory=lambda: {
            "skills": 0.45,
            "experience": 0.25,
            "projects": 0.20,
            "education": 0.10,
        }
    )

class JobDescriptionBase(BaseModel):
    jd_text: str
    role_title: Optional[str] = None
    level: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: uuid.UUID
    status: str
    structured_output: Optional[JDRubric] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[float] = None
    experience_level: Optional[float] = None
    confidence_score: Optional[float] = None
    parsed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
