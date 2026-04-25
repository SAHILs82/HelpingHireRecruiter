from __future__ import annotations
import logging

from app.schemas import JDRubric, SkillRequirement
from app.services.ai.llm_factory import llm_client
from app.services.ai.llm_prompt_repository import load_active_prompt_map, resolve_full_prompt
from app.core.llm_prompt_keys import LLM_USE_CASE_JD_PARSER
from app.prompts.jd_parser import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

FALLBACK_SYSTEM_PROMPT = SYSTEM_PROMPT

def parse_jd_to_rubric(jd_text: str, role_title: str = "AI Engineer", level: str = "junior") -> JDRubric:
    """
    Parses a job description into a structured JDRubric.
    Uses the LLM client to extract skills and requirements.
    """
    db = SessionLocal()
    try:
        active_prompts = load_active_prompt_map(db, LLM_USE_CASE_JD_PARSER)
        system_prompt = resolve_full_prompt(active_prompts, "system", FALLBACK_SYSTEM_PROMPT)
    finally:
        db.close()

    user_prompt = USER_PROMPT_TEMPLATE.format(
        role_title=role_title,
        level=level,
        jd_text=jd_text
    )
    
    try:
        rubric = llm_client.generate_structured_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=JDRubric
        )
        
        # Enforce role_title and level from the caller arguments
        rubric.role_title = role_title
        rubric.level = level
        return rubric
        
    except Exception as e:
        logger.error(f"Failed to parse JD, using fallback. Error: {e}")
        # Minimal fallback rubric to prevent pipeline crash
        return JDRubric(
            role_title=role_title,
            level=level,
            must_have_skills=[
                SkillRequirement(name="Primary technical skills", weight=0.8, mandatory=True)
            ],
            nice_to_have_skills=[],
            experience_level=0.0,
            behavioral_signals=["Problem Solving"]
        )
