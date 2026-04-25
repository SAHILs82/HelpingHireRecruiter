from __future__ import annotations

from app.models.schemas import BiasReport, CandidateScore, SkillGapReport


def adaptive_rescore(score: CandidateScore, bias: BiasReport, skill_gap: SkillGapReport) -> CandidateScore:
    adjusted = score.raw_score
    reasons = []
    if bias.risk_level == "high":
        adjusted -= 5
        reasons.append("Bias risk high; reduced confidence-weighted score")
    elif bias.risk_level == "medium":
        adjusted -= 2
        reasons.append("Bias risk medium; conservative adjustment applied")

    critical_gaps = sum(1 for gap in skill_gap.gaps if gap.gap_type == "critical")
    if critical_gaps:
        adjusted -= critical_gaps * 4
        reasons.append("Critical skill gaps lowered readiness score")

    score.raw_score = round(max(0.0, adjusted), 2)
    if reasons:
        score.reasoning_summary = f"{score.reasoning_summary} Adaptive notes: {'; '.join(reasons)}"
    return score
