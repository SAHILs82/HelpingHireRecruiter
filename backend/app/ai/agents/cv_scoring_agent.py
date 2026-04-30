"""
CV Scoring Agent
================
LangChain-powered agent that evaluates a candidate against a job description.
Follows the same architecture as cv_parser_agent.py:
  API → Agent (this file) → Service Layer

Structure:
  1. Tools Configuration (LangChain @tool decorated functions)
  2. LLM Initialization
  3. Entry-point function
"""
from __future__ import annotations

import logging
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.ai.schema.agent_cv_scoring import AgentCVScoreOutput
from app.core.config import settings
from app.ai.services.cv_scoring_service import (
    fetch_scoring_inputs,
    prepare_cv_scorer_prompts,
    verify_weighted_score,
    store_cv_score,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Tools Configuration
# -----------------------------------------------------------------------
# These are thin wrappers around the service layer. All business logic
# (verification, duplicate checks, status updates) lives in the service.
# Tools exist so a future LangGraph agent can call them autonomously.
# -----------------------------------------------------------------------

@tool
def tool_fetch_scoring_data(application_id: str) -> str:
    """Fetch candidate + JD data from the DB for scoring. Delegates to the service layer."""
    import json
    try:
        return json.dumps(fetch_scoring_inputs(application_id), default=str)
    except Exception as e:
        return f"Error: {e}"


@tool
def tool_store_score(application_id: str, response_json: str) -> str:
    """Store the LLM's scoring result to the DB. Delegates to the service layer."""
    import json
    try:
        inputs = fetch_scoring_inputs(application_id)
        agent_output = AgentCVScoreOutput.model_validate_json(response_json)
        weighting = inputs["structured_output"].get("weighting", {})
        verified_score = verify_weighted_score(agent_output, weighting)
        result = store_cv_score(
            candidate_id=inputs["candidate_id"],
            job_id=inputs["job_id"],
            application_id=inputs["application_id"],
            agent_output=agent_output,
            verified_score=verified_score,
            scoring_model=settings.llm_model,
        )
        return f"Stored score ID: {result['score_id']}, raw_score: {result['raw_score']}"
    except Exception as e:
        return f"Error: {e}"


# Attach these tools to our future agent executor or graph
CV_SCORER_TOOLS = [
    tool_fetch_scoring_data,
    tool_store_score,
]


# -----------------------------------------------------------------------
# LLM Initialization
# -----------------------------------------------------------------------

def get_llm() -> ChatOpenAI:
    """Initialize LangChain ChatOpenAI with system credentials."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.resolved_api_key,
        base_url=settings.llm_base_url,
        max_retries=settings.llm_max_retries,
        temperature=0.1,
    )


# -----------------------------------------------------------------------
# Entry-point
# -----------------------------------------------------------------------

def evaluate_candidate(application_id: str) -> Dict[str, Any]:
    """
    Entry-point called by the API layer.

    1. Fetches candidate + JD data from the DB via application_id.
    2. Prepares prompts using the service layer.
    3. Calls the LLM via LangChain with structured output.
    4. Verifies the weighted score.
    5. Stores the result to the DB.

    Returns a summary dict with score details.
    """
    # ---- Step 1: Fetch data from DB ----
    scoring_inputs = fetch_scoring_inputs(application_id)

    # ---- Step 2: Prepare prompts using business logic service ----
    system_prompt, user_prompt = prepare_cv_scorer_prompts(scoring_inputs)

    # ---- Step 3: Call LLM via LangChain ----
    try:
        llm = get_llm()

        # We use .with_structured_output to directly parse to AgentCVScoreOutput
        structured_llm = llm.with_structured_output(AgentCVScoreOutput)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "{user_prompt}"),
        ])

        chain = prompt | structured_llm

        response: AgentCVScoreOutput = chain.invoke({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        })

        # ---- Step 4: Verify weighted score ----
        weighting = scoring_inputs["structured_output"].get("weighting", {
            "skills": 0.45, "experience": 0.25, "projects": 0.20, "education": 0.10
        })
        verified_score = verify_weighted_score(response, weighting)

        # ---- Step 5: Store to DB ----
        result = store_cv_score(
            candidate_id=scoring_inputs["candidate_id"],
            job_id=scoring_inputs["job_id"],
            application_id=scoring_inputs["application_id"],
            agent_output=response,
            verified_score=verified_score,
            scoring_model=settings.llm_model,
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed to score candidate for application {application_id}, "
            f"returning failure status. Error: {e}"
        )
        return {
            "application_id": application_id,
            "status": "failed",
            "error": str(e),
        }
