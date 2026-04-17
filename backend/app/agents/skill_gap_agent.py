from __future__ import annotations

from app.models.schemas import CandidateProfile, JDRubric, SkillGapItem, SkillGapReport


def infer_skill_gaps(candidate: CandidateProfile, rubric: JDRubric) -> SkillGapReport:
    cv_lower = candidate.cv_text.lower()
    gaps = []
    for skill in rubric.must_have_skills:
        if skill.name.lower() not in cv_lower:
            gaps.append(
                SkillGapItem(
                    skill=skill.name,
                    gap_type="critical",
                    estimated_upskill_weeks=6,
                )
            )
    impact = min(1.0, len(gaps) * 0.25)
    return SkillGapReport(candidate_id=candidate.candidate_id, gaps=gaps, impact_score=impact)
