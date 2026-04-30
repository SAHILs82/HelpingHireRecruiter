import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.candidate_details import Candidate
    from app.db.models.job_description import JobDescription


class CandidateApplication(Base):
    """
    Junction table linking a candidate to a specific job description they applied for.
    """

    __tablename__ = "candidate_application"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_details.id"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_description.id"), nullable=False, index=True
    )
    
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="applied")
    # Statuses could be: applied, screening, scored, rejected, shortlisted

    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),
    )

    # Relationships
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="applications")
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="applications")
