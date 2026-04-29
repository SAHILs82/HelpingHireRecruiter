from __future__ import annotations
import logging
import uuid
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.ai.schema.agent_cv_parsing import AgentCandidateProfile
from app.core.config import settings
from app.ai.services.cv_parser_service import (
    prepare_cv_parser_prompts,
    store_parsed_candidate
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Tools Configuration
# -----------------------------------------------------------------------

@tool
def store_cv_parsed_data(candidate_id: str, cv_text: str, response_json: str) -> str:
    """
    Store the final parsed CV data into the database.
    Expects the JSON string output of the CV parser, the original cv_text, and candidate_id.
    Returns a success message with the Candidate UUID.
    """
    try:
        profile = AgentCandidateProfile.model_validate_json(response_json)
        result = store_parsed_candidate(candidate_id, cv_text, profile)
        return f"Successfully saved Candidate with ID: {result['id']}"
    except Exception as e:
        return f"Error saving Candidate to database: {e}"


# Attach these tools to our future agent executor or graph
CV_PARSER_TOOLS = [
    store_cv_parsed_data
]


def get_llm() -> ChatOpenAI:
    """Initialize LangChain ChatOpenAI with system credentials."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.resolved_api_key,
        base_url=settings.llm_base_url,
        max_retries=settings.llm_max_retries,
        temperature=0.1
    )


def parse_and_store_cv(cv_text: str, candidate_id: str | None = None) -> Dict[str, Any]:
    """
    Entry-point called by the API layer.

    1. Calls the service to prepare prompts based on the CV text.
    2. Utilizes LangChain chat models for structured generation.
    3. Calls the service to store the validated Pydantic model to the DB.
    """
    if not candidate_id:
        candidate_id = str(uuid.uuid4())

    # ---- prepare prompts using business logic service ----
    system_prompt, user_prompt = prepare_cv_parser_prompts(cv_text)

    # ---- call LLM via LangChain ----
    try:
        llm = get_llm()
        
        # We use .with_structured_output to directly parse output to AgentCandidateProfile
        structured_llm = llm.with_structured_output(AgentCandidateProfile)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "{user_prompt}")
        ])
        
        chain = prompt | structured_llm
        
        response: AgentCandidateProfile = chain.invoke({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        })
        
        # ---- store to DB ----
        result = store_parsed_candidate(candidate_id, cv_text, response)
        return result

    except Exception as e:
        logger.error(f"Failed to parse CV for candidate {candidate_id}, returning failure status. Error: {e}")
        return {
            "id": candidate_id,
            "full_name": "Extraction Failure",
            "status": "failed",
            "confidence_score": 0.0
        }
