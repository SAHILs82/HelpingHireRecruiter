# Evaluation, Reliability, and Hardening

## Evaluation suite

- Unit tests: retrieval/chunking correctness.
- Integration tests: end-to-end graph execution and final decisions.
- Eval gates: schema contract checks and decision label contract.

## Benchmarking

- Run `python scripts/benchmark_latency.py` from backend environment.
- Primary KPI: batch throughput for 100 CVs.

## Bias and safety checks

- Bias agent flags and mitigation actions captured per candidate.
- Re-evaluation loop triggers when confidence is low, bias risk is elevated, or debate disagreement is high.
- Human-review fallback path available via `needs_human_review`.

## Observability

- HTTP middleware logs latency, status code, request id, and route.
- Candidate-level audit trail can be extended in LangGraph state.
- LangSmith tracing integration is wired via `app/utils/tracing.py`.
- Enable with environment variables:
  - `LANGSMITH_TRACING=true`
  - `LANGSMITH_API_KEY=<your_key>`
  - optional `LANGSMITH_PROJECT` and `LANGSMITH_ENDPOINT`
- Trace spans are emitted for:
  - `run_hiring_graph` (full workflow)
  - `candidate_workflow` (per-candidate deep-agent pass)

## Deployment notes

- Backend: FastAPI + Uvicorn (`uvicorn app.main:app --reload`).
- Frontend: React + Vite (`cd frontend-react && npm run dev`).
- Configure backend endpoint via `VITE_API_BASE_URL` in `frontend-react/.env`.

## Production checklist

- Add authentication and RBAC before external usage.
- Encrypt CV uploads at rest and redact logs.
- Add CI pipeline with lint, typing, tests, and eval gates.
- Set retry/timeouts and worker queues for larger hiring batches.
