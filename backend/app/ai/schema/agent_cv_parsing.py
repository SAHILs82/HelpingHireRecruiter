"""
Agent CV Parsing Schema
=======================
Internal Pydantic schema used exclusively by the AI Agent for LLM processing.
This is separated from the API schemas to clarify the boundary between 
external requests and internal AI data structures.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class AgentEducation(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None

class AgentProject(BaseModel):
    title: str
    description: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    impact: Optional[str] = None

class AgentCertification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None

class AgentCandidateProfile(BaseModel):
    """
    Internal data structure used to return strictly typed data from the CV Parser Agent.
    """
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    education: List[AgentEducation] = []
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    total_experience: Optional[float] = None
    work_experience: Optional[List[Dict]] = []
    projects: List[AgentProject] = []
    certifications: List[AgentCertification] = []
    highlights: List[str] = []

    primary_domain: Optional[str] = None
    seniority_level: Optional[str] = None  # junior/mid/senior
    extra_data: Optional[Dict] = {}
    confidence_score: Optional[float] = None
