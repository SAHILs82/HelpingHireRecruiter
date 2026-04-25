"""
JD Generator Agent
==================
Takes an HR intake form (JDIntakeCreate) and produces a full JDGeneratorResponse
via the LLM. The intake form is saved to DB first, then this agent processes it.

This file orchestrates LangChain components (Model, Tools, Prompts) and relies
on `jd_generator_service` for the core business logic.
"""
from __future__ import annotations
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.schemas.agent_jd_intake import AgentJDIntake
from app.schemas.job_description import JDGeneratorResponse
from app.core.config import settings
from app.services.ai.jd_generator_service import (
    prepare_jd_generator_prompts,
    fetch_intake_from_db,
    store_generated_jd
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Tools Configuration
# -----------------------------------------------------------------------


@tool
def fetch_jd_intake_data(intake_id: str) -> str:
    """
    Fetch the raw HR intake form data from the database using its UUID.
    Returns a stringified JSON representation of the form.
    """
    try:
        intake_data = fetch_intake_from_db(intake_id)
        return intake_data.model_dump_json()
    except Exception as e:
        return f"Error fetching intake data: {e}"


@tool
def store_jd_output(jd_intake_id: str, response_json: str) -> str:
    """
    Store the final generated JD into the database and link it to the source intake form.
    Expects the JSON string output of the JD generator and the original intake_id.
    Returns the new JobDescription UUID.
    """
    try:
        # In a real LangGraph flow, this tool would likely take the Pydantic object
        # directly rather than parsing JSON, but as a generic LangChain tool string is safer.
        response = JDGeneratorResponse.model_validate_json(response_json)
        new_jd_id = store_generated_jd(jd_intake_id, response)
        return f"Successfully saved Job Description with ID: {new_jd_id}"
    except Exception as e:
        return f"Error saving JD to database: {e}"


# Attach these tools to our future agent executor or graph
JD_GENERATOR_TOOLS = [
    fetch_jd_intake_data,
    store_jd_output
]


def get_llm() -> ChatOpenAI:
    """Initialize LangChain ChatOpenAI with system credentials."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.resolved_api_key or "dummy-key",
        base_url=settings.llm_base_url,
        max_retries=settings.llm_max_retries,
        temperature=0.1
    )


def generate_job_description(intake: AgentJDIntake) -> JDGeneratorResponse:
    """
    Entry-point called by the API layer.

    1. Calls the service to prepare prompts based on the intake.
    2. Utilizes LangChain chat models for structured generation.
    3. Returns the validated Pydantic model.
    """
    # ---- prepare prompts using business logic service ----
    system_prompt, user_prompt = prepare_jd_generator_prompts(intake)

    # ---- call LLM via LangChain ----
    try:
        llm = get_llm()
        
        # We use .with_structured_output to directly parse output to JDGeneratorResponse
        structured_llm = llm.with_structured_output(JDGeneratorResponse)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "{user_prompt}")
        ])
        
        chain = prompt | structured_llm
        
        response = chain.invoke({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        })
        
        return response

    except Exception as e:
        logger.error(f"JD generation via LangChain failed: {e}")
        raise
