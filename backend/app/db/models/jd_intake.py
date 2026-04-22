"""
JD Intake Model
================
Stores the raw HR form submission *before* the agent processes it.
This is the recruiter's original input — untouched by AI.

Flow:  Frontend form → JDIntake (saved) → Agent reads it → JobDescription (generated)
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JDIntake(Base):
    """Raw recruiter intake form — every field maps 1:1 to the frontend form."""

    __tablename__ = "jd_intake"

    # ── Primary key ──────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Form fields (what the HR person fills in) ────────────
    company_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Name of the hiring company",
    )
    salary_min: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Lower bound of salary range (in local currency)",
    )
    salary_max: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Upper bound of salary range (in local currency)",
    )
    salary_currency: Mapped[str | None] = mapped_column(
        String(10), nullable=True, default="INR",
        comment="Currency code, e.g. INR, USD, EUR",
    )
    experience_min: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Minimum years of professional experience required",
    )
    experience_max: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Maximum years of experience (cap for the band)",
    )
    domain: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Industry/domain: engineering, marketing, data, design, finance, etc.",
    )
    role_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="One of: intern, full-time, part-time, contract, freelance",
    )
    preferred_education: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
        comment="One of: any, diploma, bachelors, masters, phd",
    )
    location: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
        comment="Office location or 'Remote'",
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Free-text description written by the recruiter summarizing the role",
    )



    # ── Timestamps ───────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<JDIntake id={self.id} company={self.company_name!r} "
            f"domain={self.domain!r}>"
        )
