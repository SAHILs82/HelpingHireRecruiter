"""
Agent CV Scoring Schema
=======================
Internal Pydantic schema used exclusively by the CV Scoring Agent.
The LLM returns this structured output which then maps directly
to the `cv_score` database model.

This is separated from the API schemas (app/schemas/cv_score.py) to keep
the boundary clear between what the LLM produces and what the API exposes.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class AgentEvidenceSpan(BaseModel):
    """A direct quote from the candidate's CV that supports a scoring claim."""
    claim: str = Field(
        description="What this evidence proves, e.g. 'Candidate has 3+ years Python experience'"
    )
    quote: str = Field(
        description="The exact text snippet from the CV that supports this claim"
    )
    category: str = Field(
        description="Which scoring category this evidence supports: skills, experience, projects, or education"
    )


class AgentCategoryScores(BaseModel):
    """Per-category score (0-100) aligned with the JD Rubric weighting."""
    skills: float = Field(
        ge=0.0, le=100.0,
        description="How well the candidate's skills match the JD's must-have and nice-to-have skills"
    )
    experience: float = Field(
        ge=0.0, le=100.0,
        description="How well the candidate's years and relevance of experience match the JD requirements"
    )
    projects: float = Field(
        ge=0.0, le=100.0,
        description="How well the candidate's projects demonstrate the competencies the JD demands"
    )
    education: float = Field(
        ge=0.0, le=100.0,
        description="How well the candidate's education and certifications meet the JD's education criteria"
    )


class AgentCVScoreOutput(BaseModel):
    """
    The complete structured output returned by the CV Scoring LLM Agent.
    Every field here maps to a column in the `cv_score` database table.
    """
    raw_score: float = Field(
        ge=0.0, le=100.0,
        description=(
            "The final weighted score (0-100). Must equal: "
            "(skills × skills_weight) + (experience × experience_weight) + "
            "(projects × projects_weight) + (education × education_weight)"
        )
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description=(
            "How confident the evaluator is in this score (0.0-1.0). "
            "Lower if the CV is vague, missing sections, or contradictory."
        )
    )

    category_scores: AgentCategoryScores = Field(
        description="Individual scores per category, each 0-100"
    )

    strengths: List[str] = Field(
        min_length=1, max_length=7,
        description="Top 3-7 specific reasons the candidate is a strong fit for this role"
    )
    weaknesses: List[str] = Field(
        min_length=1, max_length=7,
        description="Top 3-7 specific gaps, missing skills, or areas of concern"
    )

    evidence: List[AgentEvidenceSpan] = Field(
        min_length=2,
        description="Direct quotes from the CV that justify the category scores"
    )

    reasoning_summary: str = Field(
        min_length=100,
        description=(
            "A comprehensive paragraph (minimum 100 characters) explaining the overall evaluation. "
            "Cover why the candidate scored the way they did across all categories, "
            "highlighting the most important match/mismatch signals."
        )
    )
