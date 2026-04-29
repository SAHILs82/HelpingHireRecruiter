from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Education(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = None

class Project(BaseModel):
    title: str
    description: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    impact: Optional[str] = None

class Certification(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None

class CandidateProfile(BaseModel):
    """Core candidate profile data."""
    # 🔗 Basic Info
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # 🎓 Education
    education: List[Education] = []

    # 🛠 Skills
    skills: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Grouped skills like languages, frameworks, tools"
    )

    # 📂 Experience
    total_experience: Optional[float] = None  # years
    work_experience: Optional[List[Dict]] = []

    # 📂 Projects
    projects: List[Project] = []

    # 📜 Certifications
    certifications: List[Certification] = []

    # ⭐ Highlights / USP
    highlights: List[str] = []

    # 🧠 Derived / inferred
    primary_domain: Optional[str] = None
    seniority_level: Optional[str] = None  # junior/mid/senior

    # 🧩 Flexible
    extra_data: Optional[Dict] = {}

    # 🧪 Metadata
    confidence_score: Optional[float] = None


class CandidateUpdate(BaseModel):
    """Schema for updating an existing candidate profile. All fields optional."""
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    education: Optional[List[Education]] = None
    skills: Optional[Dict[str, List[str]]] = None
    total_experience: Optional[float] = None
    work_experience: Optional[List[Dict]] = None
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    highlights: Optional[List[str]] = None
    primary_domain: Optional[str] = None
    seniority_level: Optional[str] = None
    extra_data: Optional[Dict] = None
    confidence_score: Optional[float] = None
