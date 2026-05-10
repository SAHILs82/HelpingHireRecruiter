from __future__ import annotations

import logging
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.ai.schema.agent_skill_gap import AgentSkillGapOutput
from app.core.config import settings
from app.ai.prompts.skill_gap_analyzer import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.ai.services.skill_gap_service import (
    fetch_skill_gap_inputs, 
    store_skill_gap_report,
    execute_market_search,
    execute_github_scan
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Tools Configuration
# -----------------------------------------------------------------------

@tool
def search_market_trends(query: str) -> str:
    """
    Searches the web for current market trends, technology deprecation status, 
    or version features. Use this to check if a technology is outdated or modern.
    """
    return execute_market_search(query)

@tool
def scan_github_repo(repo_url: str, file_path: str = "") -> str:
    """
    Scans a public GitHub repository. 
    Provide the repo_url (e.g., https://github.com/user/repo).
    Optionally provide a file_path (e.g., 'package.json' or 'README.md') to fetch a specific file.
    If no file_path is provided, it fetches the root directory listing.
    """
    return execute_github_scan(repo_url, file_path)

SKILL_GAP_TOOLS = [search_market_trends, scan_github_repo]


# -----------------------------------------------------------------------
# LLM Initialization
# -----------------------------------------------------------------------

def get_llm() -> ChatOpenAI:
    """Initialize LangChain ChatOpenAI with system credentials."""
    # Note: Because of settings.llm_base_url, this can use Groq, OpenRouter, etc.
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.resolved_api_key,
        base_url=settings.llm_base_url,
        max_retries=settings.llm_max_retries,
        temperature=0.1,  # Low temp for analytical task
    )


# -----------------------------------------------------------------------
# Entry-point
# -----------------------------------------------------------------------

def analyze_skill_gap(application_id: str) -> Dict[str, Any]:
    """
    Entry-point called by the API layer.
    """
    try:
        # ---- Step 1: Fetch data from DB ----
        inputs = fetch_skill_gap_inputs(application_id)

        # ---- Step 2: Prepare LLM and Tools ----
        llm = get_llm()
        
        # Bind tools to the LLM (for create_tool_calling_agent behavior)
        # We use with_structured_output to force the final answer format, 
        # but LangChain handles tool usage internally before outputting the final schema if we set it up right.
        # Actually, to use BOTH tools and structured output, we use bind_tools or a LangGraph setup.
        # For simplicity in this agent, we will just use the structured output, but pass the tools 
        # and instruct the LLM to use them if needed. 
        # Wait, ChatOpenAI.with_structured_output overrides bind_tools. 
        # To do BOTH, we use a tool-calling agent loop. 
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        
        # We need the agent to return the structured output.
        # So we tell the agent to output the final answer as JSON matching the schema.
        schema_instructions = (
            "\\n\\nFINAL OUTPUT INSTRUCTIONS:\\n"
            "You MUST format your final answer as a raw JSON object matching this schema:\\n"
            + json.dumps(AgentSkillGapOutput.model_json_schema(), indent=2)
            + "\\nDo not wrap the JSON in markdown blocks like ```json."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + schema_instructions),
            ("user", USER_PROMPT_TEMPLATE),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # We create a standard tool-calling agent
        agent = create_openai_tools_agent(llm, SKILL_GAP_TOOLS, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=SKILL_GAP_TOOLS, verbose=True)
        
        # Format the user prompt inputs
        user_prompt_kwargs = {
            "must_have_skills": json.dumps(inputs["must_have_skills"], indent=2),
            "nice_to_have_skills": json.dumps(inputs["nice_to_have_skills"], indent=2),
            "github_url": inputs["github_url"] or "Not provided",
            "work_experience": json.dumps(inputs["work_experience"], indent=2),
            "projects": json.dumps(inputs["projects"], indent=2),
            "claimed_skills": json.dumps(inputs["claimed_skills"], indent=2),
            "scoring_weaknesses": json.dumps(inputs["cv_score_weaknesses"], indent=2),
            "cv_text": inputs["cv_text"],
        }
        
        # Run the agent
        response = agent_executor.invoke(user_prompt_kwargs)
        output_text = response["output"]
        
        # Parse the structured JSON output
        try:
            # Clean markdown formatting if the LLM ignored instructions
            if output_text.startswith("```json"):
                output_text = output_text[7:-3].strip()
            elif output_text.startswith("```"):
                output_text = output_text[3:-3].strip()
                
            agent_output = AgentSkillGapOutput.model_validate_json(output_text)
        except Exception as parse_e:
            logger.error(f"Failed to parse LLM output: {output_text}")
            raise ValueError(f"LLM did not return valid JSON schema: {parse_e}")

        # ---- Step 3: Store to DB ----
        result = store_skill_gap_report(
            application_id=inputs["application_id"],
            job_id=inputs["job_id"],
            candidate_id=inputs["candidate_id"],
            agent_output=agent_output,
            scoring_model=settings.llm_model,
        )

        return result

    except Exception as e:
        logger.error(
            f"Failed to analyze skill gap for application {application_id}, "
            f"returning failure status. Error: {e}"
        )
        return {
            "application_id": application_id,
            "status": "failed",
            "error": str(e),
        }
