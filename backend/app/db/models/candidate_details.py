import uuid
from datetime import datetime

from typing import List, TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.cv_score import CVScore
    from app.db.models.bias_report import BiasReportRecord


class Candidate(Base):
    """Persisted candidate profile."""

    __tablename__ = "candidate_details"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Basic Info
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # JSON arrays/objects mapped to JSON
    education: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    skills: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    work_experience: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    projects: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    highlights: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Derived / Other
    total_experience: Mapped[float | None] = mapped_column(nullable=True)
    primary_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cv_scores: Mapped[List["CVScore"]] = relationship("CVScore", back_populates="candidate")
    bias_reports: Mapped[list["BiasReportRecord"]] = relationship("BiasReportRecord", back_populates="candidate", cascade="all, delete")
