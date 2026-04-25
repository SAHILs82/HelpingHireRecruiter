from __future__ import annotations

from app.models.schemas import BiasReport, CandidateScore, DebateRecord


def should_rerun_evaluation(score: CandidateScore, bias: BiasReport, debate: DebateRecord) -> bool:
    if score.confidence < 0.65:
        return True
    if bias.risk_level in {"medium", "high"}:
        return True
    if debate.disagreement_score >= 0.65:
        return True
    return False
