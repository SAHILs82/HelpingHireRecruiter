from __future__ import annotations

import asyncio
from typing import Dict, List

from app.agents.adaptive_scoring_agent import adaptive_rescore
from app.agents.arbitration_agent import should_rerun_evaluation
from app.agents.bias_detection_agent import detect_bias
from app.agents.cv_scoring_agent import score_candidate
from app.agents.debate_agents import run_supporter_critic_debate
from app.agents.decision_agent import decide_candidate
from app.agents.interview_question_agent import generate_interview_questions
from app.agents.jd_parser_agent import parse_jd_to_rubric
from app.agents.skill_gap_agent import infer_skill_gaps
from app.schemas import CandidateDossier, CandidateProfile
from app.utils.tracing import traceable


@traceable(name="candidate_workflow", run_type="chain")
def _process_candidate(candidate: CandidateProfile, score, rubric) -> CandidateDossier:
    skill_gap = infer_skill_gaps(candidate, rubric)
    bias = detect_bias(candidate, score)
    debate = run_supporter_critic_debate(candidate.candidate_id, score, skill_gap)

    loops = 0
    while should_rerun_evaluation(score, bias, debate) and loops < 2:
        score = adaptive_rescore(score, bias, skill_gap)
        debate = run_supporter_critic_debate(candidate.candidate_id, score, skill_gap)
        loops += 1

    decision = decide_candidate(score, skill_gap)
    questions = generate_interview_questions(candidate, skill_gap)

    dossier = CandidateDossier(
        candidate=candidate,
        score=score,
        bias=bias,
        skill_gap=skill_gap,
        debate=debate,
        final_decision=decision,
    )
    setattr(dossier, "_interview_questions", questions)
    return dossier


@traceable(name="run_hiring_graph", run_type="chain")
async def run_hiring_graph(job_id: str, jd_text: str, candidates: List[CandidateProfile]) -> Dict[str, CandidateDossier]:
    rubric = parse_jd_to_rubric(jd_text=jd_text, role_title="AI Engineer", level="junior")

    loop = asyncio.get_event_loop()
    scoring_tasks = [loop.run_in_executor(None, score_candidate, candidate, rubric) for candidate in candidates]
    scores = await asyncio.gather(*scoring_tasks)
    score_map = {score.candidate_id: score for score in scores}

    output: Dict[str, CandidateDossier] = {}
    for candidate in candidates:
        score = score_map[candidate.candidate_id]
        output[candidate.candidate_id] = _process_candidate(candidate, score, rubric)

    return output
