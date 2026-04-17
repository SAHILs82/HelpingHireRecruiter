from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class DecisionLabel(str, Enum):
    STRONG_FIT = "strong_fit"
    BORDERLINE = "borderline"
    REJECT = "reject"
    FAST_TRACK = "fast_track"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class SkillRequirement(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    mandatory: bool = False


class JDRubric(BaseModel):
    role_title: str
    level: str
    must_have_skills: List[SkillRequirement]
    nice_to_have_skills: List[SkillRequirement] = Field(default_factory=list)
    experience_years_min: Optional[int] = None
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


class EvidenceSpan(BaseModel):
    source_chunk_id: str
    quote: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class CandidateProfile(BaseModel):
    candidate_id: str
    name: str
    email: Optional[str] = None
    total_experience_years: Optional[float] = None
    declared_skills: List[str] = Field(default_factory=list)
    cv_text: str


class CandidateScore(BaseModel):
    candidate_id: str
    raw_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    evidence: List[EvidenceSpan] = Field(default_factory=list)
    reasoning_summary: str


class BiasReport(BaseModel):
    candidate_id: str
    risk_level: Literal["low", "medium", "high"] = "low"
    bias_flags: List[str] = Field(default_factory=list)
    mitigation_actions: List[str] = Field(default_factory=list)


class SkillGapItem(BaseModel):
    skill: str
    gap_type: Literal["critical", "trainable", "non_critical"]
    estimated_upskill_weeks: Optional[int] = None


class SkillGapReport(BaseModel):
    candidate_id: str
    gaps: List[SkillGapItem] = Field(default_factory=list)
    impact_score: float = Field(ge=0.0, le=1.0, default=0.0)


class DebateRecord(BaseModel):
    candidate_id: str
    supporter_argument: str
    critic_argument: str
    unresolved_questions: List[str] = Field(default_factory=list)
    disagreement_score: float = Field(ge=0.0, le=1.0)


class FinalDecision(BaseModel):
    candidate_id: str
    label: DecisionLabel
    final_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    decision_reason: str
    next_step: str


class InterviewQuestion(BaseModel):
    candidate_id: str
    question: str
    expected_signal: str
    category: Literal["technical", "behavioral", "domain"]


class CandidateDossier(BaseModel):
    candidate: CandidateProfile
    score: CandidateScore
    bias: BiasReport
    skill_gap: SkillGapReport
    debate: Optional[DebateRecord] = None
    final_decision: Optional[FinalDecision] = None

