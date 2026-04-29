"""
CV Parser Service
=================
Contains the pure business logic and data preparation for parsing CVs.
This service is strictly decoupled from LangChain/AI orchestration frameworks.
"""
from __future__ import annotations
import logging
import uuid
from typing import Dict, Any

from app.ai.schema.agent_cv_parsing import AgentCandidateProfile
from app.services.ai.llm_prompt_repository import load_active_prompt_map, resolve_full_prompt
from app.core.llm_prompt_keys import LLM_USE_CASE_CV_PARSER
from app.ai.prompts.cv_parser import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.db.session import SessionLocal
from app.db.models.candidate_details import Candidate

logger = logging.getLogger(__name__)

FALLBACK_SYSTEM_PROMPT = SYSTEM_PROMPT


def prepare_cv_parser_prompts(cv_text: str) -> tuple[str, str]:
    """
    Business logic to prepare the prompts for the CV Parser LLM.
    Resolves the system prompt from the DB and formats the user prompt with the extracted CV text.
    
    Returns:
        tuple[str, str]: A tuple containing (system_prompt, user_prompt)
    """
    db = SessionLocal()
    try:
        active_prompts = load_active_prompt_map(db, LLM_USE_CASE_CV_PARSER)
        system_prompt = resolve_full_prompt(active_prompts, "system", FALLBACK_SYSTEM_PROMPT)
    finally:
        db.close()

    user_prompt = USER_PROMPT_TEMPLATE.format(cv_text=cv_text)
    
    return system_prompt, user_prompt


def store_parsed_candidate(candidate_id: str, cv_text: str, profile: AgentCandidateProfile) -> Dict[str, Any]:
    """
    Take the parsed LLM output (`AgentCandidateProfile`) and persist it into
    the `candidate_details` table.
    Returns a dictionary with candidate_id, full_name, status, and confidence_score.
    """
    try:
        parsed_candidate_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise ValueError(f"Invalid candidate UUID format: {candidate_id}")

    db = SessionLocal()
    try:
        candidate = Candidate(
            id=parsed_candidate_uuid,
            full_name=profile.full_name,
            email=profile.email,
            phone=profile.phone,
            linkedin_url=profile.linkedin_url,
            github_url=profile.github_url,
            portfolio_url=profile.portfolio_url,
            cv_text=cv_text,
            education=[edu.model_dump() for edu in profile.education],
            skills=profile.skills,
            work_experience=profile.work_experience,
            projects=[proj.model_dump() for proj in profile.projects],
            certifications=[cert.model_dump() for cert in profile.certifications],
            highlights=profile.highlights,
            total_experience=profile.total_experience,
            primary_domain=profile.primary_domain,
            seniority_level=profile.seniority_level,
            confidence_score=profile.confidence_score,
            extra_data=profile.extra_data
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "id": str(candidate.id),
            "full_name": candidate.full_name,
            "status": "parsed_and_saved",
            "confidence_score": candidate.confidence_score
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store generated Candidate: {e}")
        raise
    finally:
        db.close()
