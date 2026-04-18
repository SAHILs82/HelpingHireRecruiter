import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
