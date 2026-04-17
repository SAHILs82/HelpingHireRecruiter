from __future__ import annotations

from app.models.schemas import CandidateScore, DebateRecord, SkillGapReport


def run_supporter_critic_debate(candidate_id: str, score: CandidateScore, skill_gap: SkillGapReport) -> DebateRecord:
    supporter = (
        f"Candidate demonstrates practical match with score {score.raw_score} and "
        f"{len(score.evidence)} supporting evidence spans."
    )
    critic = (
        f"Candidate has {len(skill_gap.gaps)} unresolved skill gaps. "
        "Need deeper checks for production readiness."
    )

    disagreement = min(1.0, 0.25 + (len(skill_gap.gaps) * 0.2))
    unresolved = [f"Validate depth in {g.skill}" for g in skill_gap.gaps[:2]]
    return DebateRecord(
        candidate_id=candidate_id,
        supporter_argument=supporter,
        critic_argument=critic,
        unresolved_questions=unresolved,
        disagreement_score=round(disagreement, 2),
    )
