import uuid
from datetime import datetime

from typing import List, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.cv_score import CVScore
    from app.db.models.bias_report import BiasReportRecord
    from app.db.models.jd_intake import JDIntake
    from app.db.models.candidate_application import CandidateApplication


class JobDescription(Base):
    """Persisted job posting; `structured_output` stores parsed `JDRubric` (must_have_skills, weighting, etc.)."""

    __tablename__ = "job_description"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    
    # Additional expanded fields
    experience_level: Mapped[float | None] = mapped_column(nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    salary_range: Mapped[float | None] = mapped_column(nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    raw_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Foreign key linking back to the source intake form
    jd_intake_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jd_intake.id"), nullable=True,
        comment="FK to jd_intake — the recruiter form that triggered this JD generation",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cv_scores: Mapped[List["CVScore"]] = relationship("CVScore", back_populates="job")
    bias_reports: Mapped[list["BiasReportRecord"]] = relationship("BiasReportRecord", back_populates="job", cascade="all, delete")
    intake: Mapped["JDIntake | None"] = relationship("JDIntake", back_populates="job_descriptions")
    applications: Mapped[list["CandidateApplication"]] = relationship("CandidateApplication", back_populates="job", cascade="all, delete")
