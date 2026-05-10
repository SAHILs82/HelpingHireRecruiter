from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AgentSkillGapItem(BaseModel):
    """A single skill gap identified by the LLM."""
    skill: str = Field(description="The specific skill from the JD that is missing or weak")
    
    gap_type: Literal["missing", "superficial", "outdated", "context_mismatch", "needs_clarification"] = Field(
        description=(
            "missing = completely absent. "
            "superficial = listed in a skills block but zero evidence in work history/projects. "
            "outdated = technology is officially deprecated or vastly outdated compared to current market standards (use tools to verify). "
            "context_mismatch = knows the skill, but not in the required context. "
            "needs_clarification = repo scan was inconclusive or ambiguous."
        )
    )
    
    status: Literal["critical", "trainable", "non_critical"] = Field(
        description="critical = dealbreaker; trainable = can learn quickly; non_critical = nice to have"
    )
    
    evidence_reasoning: str = Field(
        description=(
            "Crucial: Explain the gap with proof. If using GitHub/Search tools, "
            "mention the results (e.g. 'Search confirmed AngularJS is deprecated'). "
            "If superficial, state 'Listed in skills, but no applied evidence found in work history'."
        )
    )
    
    estimated_upskill_weeks: int = Field(description="Estimated weeks to learn this skill on the job")


class AgentSkillGapOutput(BaseModel):
    """The complete structured output returned by the Skill Gap LLM Agent."""
    gaps: List[AgentSkillGapItem] = Field(description="List of identified skill gaps")
    
    impact_score: float = Field(
        ge=0.0, le=1.0, 
        description="Overall severity impact of these gaps. 0.0 = perfect match, 1.0 = completely unqualified"
    )
    
    summary: str = Field(
        description="A 2-3 sentence executive summary of the candidate's technical readiness and core gaps."
    )
