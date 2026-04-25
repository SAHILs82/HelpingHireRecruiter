from __future__ import annotations

from app.schemas import BiasReport, CandidateProfile, CandidateScore


def detect_bias(candidate: CandidateProfile, score: CandidateScore) -> BiasReport:
    flags = []
    risk = "low"
    text = candidate.cv_text.lower()
    if "only male team" in text or "age" in text:
        flags.append("Potentially sensitive personal attribute mention")
        risk = "medium"
    if score.confidence < 0.55:
        flags.append("Low-confidence score can amplify noisy proxies")
        risk = "medium"

    mitigations = ["Run fairness rerun without sensitive proxies"] if risk != "low" else []
    return BiasReport(
        candidate_id=candidate.candidate_id,
        risk_level=risk,  # type: ignore[arg-type]
        bias_flags=flags,
        mitigation_actions=mitigations,
    )
