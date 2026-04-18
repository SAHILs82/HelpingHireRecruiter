"""update jobs table to job_description

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename table
    op.rename_table("jobs", "job_description")
    
    # Rename column
    op.alter_column("job_description", "rubric", new_column_name="structured_output")
    
    # Add new columns
    op.add_column("job_description", sa.Column("experience_level", sa.Float(), nullable=True))
    op.add_column("job_description", sa.Column("company_name", sa.String(length=255), nullable=True))
    op.add_column("job_description", sa.Column("location", sa.String(length=255), nullable=True))
    op.add_column("job_description", sa.Column("employment_type", sa.String(length=50), nullable=True))
    op.add_column("job_description", sa.Column("salary_range", sa.Float(), nullable=True))
    op.add_column("job_description", sa.Column("source", sa.String(length=100), nullable=True))
    op.add_column("job_description", sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("job_description", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column("job_description", sa.Column("confidence_score", sa.Float(), nullable=True))
    op.add_column("job_description", sa.Column("raw_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Drop columns
    op.drop_column("job_description", "raw_output")
    op.drop_column("job_description", "confidence_score")
    op.drop_column("job_description", "error_message")
    op.drop_column("job_description", "parsed_at")
    op.drop_column("job_description", "source")
    op.drop_column("job_description", "salary_range")
    op.drop_column("job_description", "employment_type")
    op.drop_column("job_description", "location")
    op.drop_column("job_description", "company_name")
    op.drop_column("job_description", "experience_level")
    
    # Revert rename column
    op.alter_column("job_description", "structured_output", new_column_name="rubric")
    
    # Revert rename table
    op.rename_table("job_description", "jobs")
