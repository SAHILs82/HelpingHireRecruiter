"""
Agent JD Intake Schema
======================
Internal Pydantic schema used exclusively by the AI Agent for LLM processing.
This is separated from the API schemas to clarify the boundary between 
external requests and internal AI data structures.
"""
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

# Allowed values for constraints (shared domain knowledge)
RoleType = Literal["intern", "full-time", "part-time", "contract", "freelance"]
PreferredEducation = Literal["any", "diploma", "bachelors", "masters", "phd"]


class AgentJDIntake(BaseModel):
    """
    Internal data structure used to cleanly pass database contents into the JD Generator Agent.
    This guarantees the AI receives strictly typed data during processing.
    """
    company_name: Optional[str] = Field(
        default=None, max_length=255,
        description="Name of the hiring company.",
    )
    salary_min: Optional[float] = Field(
        default=None, ge=0,
        description="Lower bound of salary range.",
    )
    salary_max: Optional[float] = Field(
        default=None, ge=0,
        description="Upper bound of salary range.",
    )
    experience_min: Optional[float] = Field(
        default=None, ge=0,
        description="Minimum years of professional experience.",
    )
    experience_max: Optional[float] = Field(
        default=None, ge=0,
        description="Maximum years of experience.",
    )
    domain: Optional[str] = Field(
        default=None, max_length=100,
        description="Industry domain: engineering, marketing, data, design, finance, etc.",
    )
    role_type: Optional[RoleType] = Field(
        default=None,
        description="Type of employment: intern, full-time, part-time, contract, freelance.",
    )
    preferred_education: Optional[PreferredEducation] = Field(
        default=None,
        description="Minimum education level: any, diploma, bachelors, masters, phd.",
    )
    location: Optional[str] = Field(
        default=None, max_length=255,
        description="Job location or 'Remote'.",
    )
    description: str = Field(
        ...,
        min_length=20,
        description=(
            "Free-text description of the role. Include what the hire will do, "
            "key skills needed, team context, and any other relevant details."
        ),
    )

    @property
    def salary_range_str(self) -> str:
        """Build a human-readable salary string for prompts."""
        if self.salary_min is not None and self.salary_max is not None:
            return f"{self.salary_min:,.0f} - {self.salary_max:,.0f} INR"
        if self.salary_min is not None:
            return f"{self.salary_min:,.0f}+ INR"
        return "Not provided"

    @property
    def experience_range_str(self) -> str:
        """Build a human-readable experience range for prompts."""
        if self.experience_min is not None and self.experience_max is not None:
            return f"{self.experience_min:.0f} - {self.experience_max:.0f} years"
        if self.experience_min is not None:
            return f"{self.experience_min:.0f}+ years"
        return "Not provided"

    @field_validator("salary_max")
    @classmethod
    def salary_max_gte_min(cls, v: Optional[float], info) -> Optional[float]:
        salary_min = info.data.get("salary_min")
        if v is not None and salary_min is not None and v < salary_min:
            raise ValueError("salary_max must be >= salary_min")
        return v

    @field_validator("experience_max")
    @classmethod
    def experience_max_gte_min(cls, v: Optional[float], info) -> Optional[float]:
        exp_min = info.data.get("experience_min")
        if v is not None and exp_min is not None and v < exp_min:
            raise ValueError("experience_max must be >= experience_min")
        return v
