import uuid
from datetime import datetime
from typing import TYPE_CHECKING
import sqlalchemy

from sqlalchemy import DateTime, String, Text, func, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.cv_score import CVScore
    from app.db.models.job_description import JobDescription
    from app.db.models.candidate_details import Candidate

class BiasReportRecord(Base):
    """
    Stores the output of the Bias Detection Agent.
    One report per CVScore evaluation — audits the scoring rationale for fairness.
    """

    __tablename__ = "bias_report"

    # ─── Primary Key ───
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ─── Foreign Keys (Links to the evaluation being audited) ───
    cv_score_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cv_score.id"), nullable=False
    )
    # WHY: This is the most important FK. It directly links THIS bias report
    #      to the SPECIFIC scoring evaluation it is auditing in cv_score.py.

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_description.id"), nullable=False
    )
    # WHY: Allows querying "Show me all bias reports for this job posting."
    #      Useful for detecting if a particular JD's wording is causing biased evaluations.

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("candidate_details.id"), nullable=False
    )
    # WHY: Allows querying "Were any candidates unfairly treated across ALL jobs?"

    # ─── Core Bias Detection Output ───
    risk_level: Mapped[str] = mapped_column(
        sqlalchemy.Enum("low", "medium", "high", name="risk_level_enum"), 
        nullable=False, 
        default="low"
    )
    # WHY: The headline verdict. Used by the LangGraph router (should_reevaluate) 
    #      to decide if we need to loop back and re-score the candidate.

    bias_flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # WHY: The specific phrases or patterns the detector found problematic (the evidence).

    bias_categories: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # WHY: Categorizes WHAT TYPE of bias was detected (e.g. "gender", "age_proxy", "education_pedigree").
    #      This is critical for HR Dashboard analytics.

    mitigation_actions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # WHY: Actionable suggestions (e.g., "Re-evaluate without considering university name").
    #      These are passed back to the Adaptive Scorer Agent in the feedback loop.

    detection_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    # WHY: How confident the Bias Detector is about its findings (0.0 - 1.0).

    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    # WHY: The full explanation from the Bias Detector LLM on why it flagged things.

    reviewed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # WHY: Stores the exact text (from CVScore reasoning_summary) that was audited.
    #      Acts as an audit trail snapshot in case the CVScore is later overwritten.

    # ─── Agent Metadata ───
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # WHY: Tracks LangGraph feedback loops. version=1 is the first check, 
    #      version=2 is the check after the Adaptive Scorer has re-scored.

    detected_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detection_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # WHY: Keeps track of which LLM agent/model ran this detection (e.g., 'gpt-4o-mini').

    # ─── Timestamps ───
    detected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    # ─── Relationships ───
    cv_score: Mapped["CVScore"] = relationship("CVScore", back_populates="bias_reports")
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="bias_reports")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="bias_reports")
