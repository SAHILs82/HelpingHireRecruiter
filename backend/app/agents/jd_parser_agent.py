from __future__ import annotations

from app.models.schemas import JDRubric, SkillRequirement


def parse_jd_to_rubric(jd_text: str, role_title: str = "AI Engineer", level: str = "junior") -> JDRubric:
    # Production note: swap this with a structured LLM chain + parser.
    must_have = [
        SkillRequirement(name="Python", weight=0.2, mandatory=True),
        SkillRequirement(name="LangChain", weight=0.2, mandatory=True),
        SkillRequirement(name="RAG", weight=0.15, mandatory=True),
        SkillRequirement(name="API development", weight=0.15, mandatory=True),
    ]
    nice_to_have = [
        SkillRequirement(name="LangGraph", weight=0.1, mandatory=False),
        SkillRequirement(name="Docker", weight=0.1, mandatory=False),
        SkillRequirement(name="Evaluation frameworks", weight=0.1, mandatory=False),
    ]
    if "fastapi" in jd_text.lower():
        must_have.append(SkillRequirement(name="FastAPI", weight=0.1, mandatory=True))

    return JDRubric(
        role_title=role_title,
        level=level,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        experience_years_min=1,
        behavioral_signals=["ownership", "communication", "problem solving"],
    )
