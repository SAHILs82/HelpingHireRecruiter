"""
JD Generator Service
====================
Contains the pure business logic and data preparation for generating Job Descriptions.
This service is strictly decoupled from LangChain/AI orchestration frameworks.
"""
from __future__ import annotations
import logging

import re
from datetime import datetime, UTC
from uuid import UUID

from app.schemas.agent_jd_intake import AgentJDIntake
from app.schemas.job_description import JDGeneratorResponse
from app.services.ai.llm_prompt_repository import load_active_prompt_map, resolve_full_prompt
from app.core.llm_prompt_keys import LLM_USE_CASE_JD_GENERATOR
from app.prompts.jd_generator import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.db.session import SessionLocal
from app.db.models.jd_intake import JDIntake
from app.db.models.job_description import JobDescription

logger = logging.getLogger(__name__)

FALLBACK_SYSTEM_PROMPT = SYSTEM_PROMPT

def prepare_jd_generator_prompts(intake: AgentJDIntake) -> tuple[str, str]:
    """
    Business logic to prepare the prompts for the JD Generator LLM.
    Resolves the system prompt from the DB and formats the user prompt with form fields.
    
    Returns:
        tuple[str, str]: A tuple containing (system_prompt, user_prompt)
    """
    db = SessionLocal()
    try:
        active_prompts = load_active_prompt_map(db, LLM_USE_CASE_JD_GENERATOR)
        system_prompt = resolve_full_prompt(active_prompts, "system", FALLBACK_SYSTEM_PROMPT)
    finally:
        db.close()

    user_prompt = USER_PROMPT_TEMPLATE.format(
        company_name=intake.company_name or "Not provided",
        salary_range=intake.salary_range_str,
        experience_range=intake.experience_range_str,
        domain=intake.domain or "Not specified",
        role_type=intake.role_type or "Not specified",
        preferred_education=intake.preferred_education or "Not specified",
        location=intake.location or "Not specified",
        description=intake.description,
    )
    
    return system_prompt, user_prompt


def fetch_intake_from_db(intake_id: str) -> AgentJDIntake:
    """
    Fetch raw HR intake from `jd_intake` table and map it to `AgentJDIntake`
    for LLM processing.
    """
    try:
        parsed_uuid = UUID(intake_id)
    except ValueError:
        raise ValueError(f"Invalid UUID format: {intake_id}")

    db = SessionLocal()
    try:
        db_intake = db.query(JDIntake).filter(JDIntake.id == parsed_uuid).first()
        if not db_intake:
            raise ValueError(f"No JD Intake found with ID {intake_id}")

        return AgentJDIntake(
            company_name=db_intake.company_name,
            salary_min=db_intake.salary_min,
            salary_max=db_intake.salary_max,
            experience_min=db_intake.experience_min,
            experience_max=db_intake.experience_max,
            domain=db_intake.domain,
            role_type=db_intake.role_type,
            preferred_education=db_intake.preferred_education,
            location=db_intake.location,
            description=db_intake.description,
        )
    finally:
        db.close()


def store_generated_jd(jd_intake_id: str, response: JDGeneratorResponse) -> str:
    """
    Take the parsed LLM output (`JDGeneratorResponse`) and persist it into
    the `job_description` table, linking it back to the original `jd_intake_id`.
    Returns the new JobDescription ID.
    """
    try:
        parsed_intake_uuid = UUID(jd_intake_id)
    except ValueError:
        raise ValueError(f"Invalid intake UUID format: {jd_intake_id}")

    # Parse float salary securely if needed (e.g. from "50,000 - 80,000 INR" string)
    parsed_salary = None
    if response.salary_range:
        numbers = re.findall(r'\d[\d,]*', response.salary_range)
        if numbers:
            try:
                # Get the first match, remove commas, turn to float
                parsed_salary = float(numbers[0].replace(",", ""))
            except ValueError:
                pass


    db = SessionLocal()
    try:
        new_jd = JobDescription(
            jd_intake_id=parsed_intake_uuid,
            role_title=response.role_title,
            level=response.level,
            experience_level=response.experience_level,
            company_name=response.company_name,
            location=response.location,
            employment_type=response.employment_type,
            salary_range=parsed_salary,
            jd_text=response.jd_text,
            structured_output=response.structured_output.model_dump(),
            status=response.status,
            confidence_score=response.confidence_score,
            raw_output=response.model_dump(),
            source="jd_generator_agent",
            parsed_at=datetime.now(UTC),
        )
        db.add(new_jd)
        db.commit()
        db.refresh(new_jd)
        return str(new_jd.id)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store generated JD: {e}")
        raise
    finally:
        db.close()
