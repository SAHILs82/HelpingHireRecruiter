from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────────────────
#  JD GENERATOR — LLM output schemas
# ──────────────────────────────────────────────────────────

class JDGeneratorStructuredOutput(BaseModel):
    """Structured hiring signals extracted by the LLM."""
    must_have_skills: List[str]
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    tools_and_technologies: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience_required: float = 0.0
    behavioral_signals: List[str] = Field(default_factory=list)
    weighting: Dict[str, float] = Field(
        default_factory=lambda: {
            "skills": 0.45,
            "experience": 0.25,
            "projects": 0.20,
            "education": 0.10,
        }
    )

    @field_validator("weighting")
    @classmethod
    def weighting_must_sum_to_one(cls, v: Dict[str, float]) -> Dict[str, float]:
        total = sum(v.values())
        if not (0.95 <= total <= 1.05):  # small tolerance for float rounding
            raise ValueError(f"weighting values must sum to 1.0, got {total}")
        return v


class JDGeneratorResponse(BaseModel):
    """Top-level output returned by the JD generation agent."""
    role_title: str
    level: str
    experience_level: float = 0.0
    company_name: Optional[str] = None
    location: str = "Not Specified"
    employment_type: str = "full-time"
    salary_range: Optional[str] = None
    jd_text: str
    structured_output: JDGeneratorStructuredOutput
    status: str = "active"
    confidence_score: float = Field(ge=0.0, le=1.0)

