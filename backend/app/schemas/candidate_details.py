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
    candidate_id: str
    cv_text: str
    
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
