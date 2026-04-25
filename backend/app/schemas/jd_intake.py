"""
JD Intake Schemas
=================
Pydantic schemas for the JD Intake API layer.
Maps 1:1 with the frontend TypeScript interfaces in jdIntakeSchema.ts.

- JDIntakeCreate   → used when the recruiter submits a new form (API)
- JDIntakeUpdate   → used when the recruiter updates a draft (API)
- JDIntakeResponse → returned to the frontend after create/read (API)
"""
from __future__ import annotations

import uuid
from typing import Optional, Literal

from pydantic import BaseModel, Field


# Allowed values for constraints
RoleType = Literal["intern", "full-time", "part-time", "contract", "freelance"]
PreferredEducation = Literal["any", "diploma", "bachelors", "masters", "phd"]


# ──────────────────────────────────────────────────────────
#  API Schemas (Frontend ↔ Backend)
# ──────────────────────────────────────────────────────────

class JDIntakeCreate(BaseModel):
    """Schema for creating a new JD Intake form submission."""
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
        description="Free-text description of the role written by the recruiter.",
    )


class JDIntakeUpdate(BaseModel):
    """Schema for updating an existing JD Intake draft. All fields optional."""
    company_name: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    domain: Optional[str] = None
    role_type: Optional[RoleType] = None
    preferred_education: Optional[PreferredEducation] = None
    location: Optional[str] = None
    description: Optional[str] = None


class JDIntakeResponse(BaseModel):
    """Schema returned to the frontend after create/read operations."""
    id: uuid.UUID
    company_name: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    domain: Optional[str] = None
    role_type: Optional[str] = None
    preferred_education: Optional[str] = None
    location: Optional[str] = None
    description: str

    model_config = {"from_attributes": True}
