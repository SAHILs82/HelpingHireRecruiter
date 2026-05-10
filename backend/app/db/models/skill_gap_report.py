import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Float, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.candidate_application import CandidateApplication
    from app.db.models.job_description import JobDescription
    from app.db.models.candidate_details import Candidate

class SkillGapReportRecord(Base):
    """
    Persists the result of the Skill Gap Agent.
    Links directly to an application to evaluate the candidate's gaps against the specific job requirements.
    """

    __tablename__ = "skill_gap_report"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # ─── Foreign Keys ───
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_application.id"), nullable=False, unique=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_description.id"), nullable=False
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_details.id"), nullable=False
    )

    # ─── Core Output ───
    # Storing the list of gaps as JSONB to allow dynamic schema evolution if needed
    gaps: Mapped[list | None] = mapped_column(JSONB, nullable=False)
    
    impact_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Agent Metadata ───
    analyzed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_model: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Timestamps ───
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ─── Relationships ───
    application: Mapped["CandidateApplication"] = relationship("CandidateApplication", back_populates="skill_gap_report", lazy="noload")
    job: Mapped["JobDescription"] = relationship("JobDescription", lazy="noload")
    candidate: Mapped["Candidate"] = relationship("Candidate", lazy="noload")
