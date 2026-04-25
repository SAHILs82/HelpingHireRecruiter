from __future__ import annotations

from typing import List

from app.models.schemas import CandidateProfile, InterviewQuestion, SkillGapReport


def generate_interview_questions(
    candidate: CandidateProfile, skill_gap: SkillGapReport
) -> List[InterviewQuestion]:
    questions: List[InterviewQuestion] = [
        InterviewQuestion(
            candidate_id=candidate.candidate_id,
            question="Describe one production system you designed end-to-end and your trade-offs.",
            expected_signal="System design depth and decision quality",
            category="technical",
        ),
        InterviewQuestion(
            candidate_id=candidate.candidate_id,
            question="Tell us about a difficult bug and how you resolved it.",
            expected_signal="Debugging method and ownership",
            category="behavioral",
        ),
    ]
    for gap in skill_gap.gaps[:3]:
        questions.append(
            InterviewQuestion(
                candidate_id=candidate.candidate_id,
                question=f"You appear to have limited experience in {gap.skill}. How would you ramp up quickly?",
                expected_signal="Learning velocity and practical planning",
                category="domain",
            )
        )
    return questions
