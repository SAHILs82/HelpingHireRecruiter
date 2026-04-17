from __future__ import annotations

from typing import Dict, List, TypedDict

from app.models.schemas import (
    BiasReport,
    CandidateDossier,
    CandidateProfile,
    CandidateScore,
    DebateRecord,
    FinalDecision,
    InterviewQuestion,
    JDRubric,
    SkillGapReport,
)


class HiringState(TypedDict, total=False):
    job_id: str
    jd_text: str
    rubric: JDRubric
    candidates: List[CandidateProfile]
    candidate_scores: Dict[str, CandidateScore]
    bias_reports: Dict[str, BiasReport]
    skill_gap_reports: Dict[str, SkillGapReport]
    debate_records: Dict[str, DebateRecord]
    final_decisions: Dict[str, FinalDecision]
    interview_questions: Dict[str, List[InterviewQuestion]]
    audit_log: List[str]
    confidence_metrics: Dict[str, float]
    dossiers: Dict[str, CandidateDossier]
