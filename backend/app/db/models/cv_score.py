import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.job_description import JobDescription
    from app.db.models.candidate_details import Candidate

class CVScore(Base):
    """
    Persists the scoring result of a candidate against a job description.
    Acts as a junction table between job_description and candidate_details with versioning.
    """

    __tablename__ = "cv_score"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_description.id"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidate_details.id"), nullable=False)

    # Core scoring outputs
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    
    strengths: Mapped[list | None] = mapped_column(JSONB, nullable=True) # List[str]
    weaknesses: Mapped[list | None] = mapped_column(JSONB, nullable=True) # List[str]
    evidence: Mapped[list | None] = mapped_column(JSONB, nullable=True) # List[EvidenceSpan]
    reasoning_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Granular breakdown (by JDRubric weighting categories)
    category_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True) # {"skills": 80, "experience": 70...}

    # Agent metadata
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scored") # scored, rescored, failed
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    scored_by: Mapped[str | None] = mapped_column(String(100), nullable=True) # agent identifier
    scoring_model: Mapped[str | None] = mapped_column(String(100), nullable=True) # LLM used

    # Timestamps
    scored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="cv_scores")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="cv_scores")
