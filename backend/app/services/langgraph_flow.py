from __future__ import annotations

from typing import Dict

from app.agents.adaptive_scoring_agent import adaptive_rescore
from app.agents.bias_detection_agent import detect_bias
from app.agents.cv_scoring_agent import score_candidate
from app.agents.debate_agents import run_supporter_critic_debate
from app.agents.decision_agent import decide_candidate
from app.agents.interview_question_agent import generate_interview_questions
from app.agents.jd_parser_agent import parse_jd_to_rubric
from app.agents.skill_gap_agent import infer_skill_gaps
from app.models.state import HiringState


def jd_parser_node(state: HiringState) -> HiringState:
    state["rubric"] = parse_jd_to_rubric(state["jd_text"])
    state.setdefault("audit_log", []).append("jd_parser_node completed")
    return state


def scorer_node(state: HiringState) -> HiringState:
    rubric = state["rubric"]
    score_map = {}
    for candidate in state["candidates"]:
        score_map[candidate.candidate_id] = score_candidate(candidate, rubric)
    state["candidate_scores"] = score_map
    state.setdefault("audit_log", []).append("scorer_node completed")
    return state


def skill_gap_node(state: HiringState) -> HiringState:
    rubric = state["rubric"]
    reports = {}
    for candidate in state["candidates"]:
        reports[candidate.candidate_id] = infer_skill_gaps(candidate, rubric)
    state["skill_gap_reports"] = reports
    state.setdefault("audit_log", []).append("skill_gap_node completed")
    return state


def bias_node(state: HiringState) -> HiringState:
    reports = {}
    for candidate in state["candidates"]:
        cid = candidate.candidate_id
        reports[cid] = detect_bias(candidate, state["candidate_scores"][cid])
    state["bias_reports"] = reports
    state.setdefault("audit_log", []).append("bias_node completed")
    return state


def adaptive_scoring_node(state: HiringState) -> HiringState:
    for candidate in state["candidates"]:
        cid = candidate.candidate_id
        state["candidate_scores"][cid] = adaptive_rescore(
            state["candidate_scores"][cid],
            state["bias_reports"][cid],
            state["skill_gap_reports"][cid],
        )
    state.setdefault("audit_log", []).append("adaptive_scoring_node completed")
    return state


def debate_node(state: HiringState) -> HiringState:
    debates = {}
    for candidate in state["candidates"]:
        cid = candidate.candidate_id
        debates[cid] = run_supporter_critic_debate(
            cid,
            state["candidate_scores"][cid],
            state["skill_gap_reports"][cid],
        )
    state["debate_records"] = debates
    state.setdefault("audit_log", []).append("debate_node completed")
    return state


def decision_node(state: HiringState) -> HiringState:
    decisions: Dict[str, object] = {}
    for candidate in state["candidates"]:
        cid = candidate.candidate_id
        decisions[cid] = decide_candidate(state["candidate_scores"][cid], state["skill_gap_reports"][cid])
    state["final_decisions"] = decisions  # type: ignore[assignment]
    state.setdefault("audit_log", []).append("decision_node completed")
    return state


def interview_node(state: HiringState) -> HiringState:
    output = {}
    for candidate in state["candidates"]:
        cid = candidate.candidate_id
        output[cid] = generate_interview_questions(candidate, state["skill_gap_reports"][cid])
    state["interview_questions"] = output
    state.setdefault("audit_log", []).append("interview_node completed")
    return state
