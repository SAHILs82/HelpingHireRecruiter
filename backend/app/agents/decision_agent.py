from __future__ import annotations

from app.models.schemas import CandidateScore, DecisionLabel, FinalDecision, SkillGapReport


def decide_candidate(score: CandidateScore, skill_gap: SkillGapReport) -> FinalDecision:
    critical_gap_count = sum(1 for g in skill_gap.gaps if g.gap_type == "critical")
    final_score = max(0.0, score.raw_score - (critical_gap_count * 8))

    if score.confidence < 0.6:
        label = DecisionLabel.NEEDS_HUMAN_REVIEW
        next_step = "Manual panel review"
    elif final_score >= 85 and critical_gap_count == 0:
        label = DecisionLabel.FAST_TRACK
        next_step = "Skip to final round"
    elif final_score >= 70:
        label = DecisionLabel.STRONG_FIT if critical_gap_count == 0 else DecisionLabel.BORDERLINE
        next_step = "Technical + behavioral interview"
    else:
        label = DecisionLabel.REJECT
        next_step = "Reject with feedback"

    return FinalDecision(
        candidate_id=score.candidate_id,
        label=label,
        final_score=round(final_score, 2),
        confidence=score.confidence,
        decision_reason="Derived from score, confidence, and skill-gap criticality.",
        next_step=next_step,
    )
