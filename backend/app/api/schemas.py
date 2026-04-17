from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CandidateInput(BaseModel):
    candidate_id: str
    name: str
    email: str | None = None
    cv_text: str = Field(min_length=30)
    total_experience_years: float | None = None
    declared_skills: List[str] = Field(default_factory=list)


class ScreeningRequest(BaseModel):
    job_id: str
    jd_text: str
    candidates: List[CandidateInput] = Field(default_factory=list)
