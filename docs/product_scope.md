# Product Scope and Success Metrics

## User roles

- Recruiter: posts jobs, uploads CV batches, reviews shortlist, exports interview kits.
- Candidate: browses openings, uploads CV, checks fit probability and skill gaps.
- Admin: manages policies, prompt versions, retention settings, and audit access.

## Panels

## Recruiter panel

- Job post creation with editable rubric weights.
- CV upload (single and batch).
- Ranked list with explainable score and evidence citations.
- Bias warnings, skill-gap matrix, debate transcript, and recommended next steps.

## Candidate panel

- Open roles listing.
- CV upload and role-fit probability simulation.
- Match/mismatch explanation and improvement recommendations.
- What-if resubmission flow with updated CV.

## Key success metrics

- `shortlist_precision_at_10 >= 0.8` on gold evaluation set.
- `decision_with_citations_rate >= 0.95`.
- `p95_batch_latency_100_cvs <= 120s` for score-only pipeline.
- `malformed_json_recovery_rate >= 0.98`.
- `human_review_escalation_rate <= 15%` with calibrated confidence thresholds.

## Non-functional requirements

- Full traceability per candidate decision.
- Policy-driven fairness checks and re-evaluation.
- PII redaction in logs and role-based access control.
- Idempotent processing for repeated uploads.
