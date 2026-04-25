from __future__ import annotations

from app.schemas import CandidateProfile, CandidateScore, JDRubric
from app.services.evidence_service import retrieve_candidate_evidence


def _skill_hit_count(cv_text: str, rubric: JDRubric) -> tuple[int, int]:
    text = cv_text.lower()
    required = [s.name.lower() for s in rubric.must_have_skills]
    hits = sum(1 for skill in required if skill in text)
    return hits, len(required)


def score_candidate(candidate: CandidateProfile, rubric: JDRubric) -> CandidateScore:
    hits, total = _skill_hit_count(candidate.cv_text, rubric)
    ratio = hits / total if total else 0.0
    raw_score = round(min(100.0, 45 + ratio * 45), 2)
    confidence = round(min(1.0, 0.55 + ratio * 0.35), 2)

    evidence = retrieve_candidate_evidence(
        candidate_id=candidate.candidate_id,
        cv_text=candidate.cv_text,
        query=" ".join(s.name for s in rubric.must_have_skills),
    )
    strengths = [f"Matched {hits}/{total} must-have skills"] if total else []
    weaknesses = ["Missing role-specific required tools"] if ratio < 0.7 else []

    return CandidateScore(
        candidate_id=candidate.candidate_id,
        raw_score=raw_score,
        confidence=confidence,
        strengths=strengths,
        weaknesses=weaknesses,
        evidence=evidence,
        reasoning_summary=f"Score based on must-have match ratio ({hits}/{total}) and evidence quality.",
    )
