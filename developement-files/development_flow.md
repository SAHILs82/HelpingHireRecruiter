# 🚀 Deep Agents — Development Flow Guide

> **Purpose**: Step-by-step execution roadmap to build your AI hiring screener, progressing from
> individual agents → deep agent orchestration → backend API wiring → frontend connection.
>
> **Based on**: [implementation_plan.md](./implementation_plan.md) | **Current Completion**: ~25%

---

## 📋 How to Use This Document

Each stage below has:
- ✅ **Checkboxes** — tick them off as you complete each item
- 📁 **Files to touch** — exact paths relative to `backend/app/`
- 🧪 **Verification step** — how to confirm the stage works before moving on
- 🔗 **Dependencies** — what must be done before this stage

---

## Overview — The 5 Stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   STAGE 1          STAGE 2          STAGE 3         STAGE 4   STAGE 5   │
│  ┌─────────┐     ┌──────────┐    ┌──────────┐   ┌────────┐  ┌───────┐  │
│  │  AGENTS  │ ──▶ │   DEEP   │ ──▶ │ BACKEND  │ ──▶│CONNECT │──▶│POLISH │  │
│  │ (Single  │    │  AGENTS  │    │   API    │   │FRONTEND│  │ & EVAL│  │
│  │  LLM     │    │ (Graph + │    │ (FastAPI │   │(React  │  │      │  │
│  │  Calls)  │    │  Loops)  │    │  + RAG)  │   │  UI)   │  │      │  │
│  └─────────┘     └──────────┘    └──────────┘   └────────┘  └───────┘  │
│                                                                         │
│   Days 1-4        Days 5-8        Days 9-11      Days 12-15  Days 16-21 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Why this order?**
1. You can't orchestrate agents if individual agents don't work yet
2. You can't build API endpoints if the pipeline they call doesn't exist
3. You can't connect frontend if the backend doesn't serve data

---

## 🟥 Stage 1: Individual Agents — Make Every Agent Real (Days 1-4)

> **Goal**: Replace every hardcoded/placeholder agent with real LLM calls that produce structured Pydantic outputs.
> This is the foundation — nothing works without this.

### 🔗 Dependencies: None (this is the starting point)

---

### Step 1.1 — Build the Central LLM Client

> _Currently `core/llm.py` is a placeholder returning `"placeholder response"`. This needs to become a real client._

- [ ] **`core/llm.py`** — Build a production-grade LLM client factory:
  - OpenRouter / OpenAI API client (using `openai` SDK or `langchain_openai`)
  - API key loaded from `core/config.py` settings (use `.env` file)
  - Retry with exponential backoff (3 attempts, 1s → 2s → 4s)
  - Timeout handling (30s default per call)
  - Structured JSON output parsing → validate against Pydantic schema
  - Token counting & cost tracking per call
  - Fallback: if LLM call fails after retries → return a `ModelFailure` sentinel
  - Logging: log every call (model, tokens_in, tokens_out, latency_ms)

```python
# Rough structure for core/llm.py
from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    def __init__(self, api_key, model, base_url):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def generate_structured(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        output_schema: type[BaseModel]
    ) -> BaseModel:
        # 1. Call LLM with JSON mode
        # 2. Parse response into output_schema
        # 3. Track tokens + cost
        ...
```

- [ ] **`core/config.py`** — Ensure settings include:
  - `OPENROUTER_API_KEY` or `OPENAI_API_KEY`
  - `LLM_MODEL` (e.g., `"google/gemma-2-9b-it"` or `"gpt-4o-mini"`)
  - `LLM_BASE_URL` (e.g., `"https://openrouter.ai/api/v1"`)
  - `LLM_TIMEOUT_SECONDS` = 30
  - `LLM_MAX_RETRIES` = 3

- [ ] **`.env`** — Create from `.env.example` with real API key

**🧪 Verification**: Write a quick test script that calls `LLMClient.generate_structured()` with a simple prompt and confirms you get a valid Pydantic object back.

---

### Step 1.2 — Build the Prompt Registry

> _Currently `prompts/*.py` files are 1-3 line placeholders. Each needs a real system prompt, user prompt template, and output schema._

For **each** prompt file, export three things:
```python
SYSTEM_PROMPT = "..."        # The system instruction
USER_PROMPT_TEMPLATE = "..."  # Template with {variables}
OUTPUT_SCHEMA = SomePydanticModel  # Expected output structure
```

**Prompt files to build** (in order of the pipeline):

- [ ] **`prompts/jd_parser.py`** — Parse job description into structured rubric
  - Input: `{jd_text}`, `{role_title}`, `{level}`
  - Output: `JDRubric` (must_have_skills, nice_to_have_skills, experience_years, behavioral_signals)
  - Key prompt technique: **Few-shot examples** of JD → rubric conversion

- [ ] **`prompts/cv_parser.py`** — Extract all structured information from candidate side
  - Input: `{cv_text}`
  - Output: `ParsedCV` (full profile extraction including education, experience, and contact)
  - Key prompt technique: **Entity extraction** with strictly defined YAML/JSON output

- [ ] **`prompts/cv_scorer.py`** — Preference matching: score candidate CV against recruiter preferences
  - Input: `{rubric_json}`, `{cv_text}` or `{parsed_cv_json}`, `{evidence_chunks}`
  - Output: `CandidateScore` (overall_score, per_skill_scores, evidence_citations, confidence)
  - Key prompt technique: **Chain-of-thought** ("Think step by step...")

- [ ] **`prompts/bias_detector.py`** — Detect bias proxies in scoring rationale
  - Input: `{candidate_name}`, `{scoring_rationale}`, `{score_breakdown}`
  - Output: `BiasReport` (risk_level, bias_indicators, mitigation_suggestions)
  - Key prompt technique: **Constitutional AI** pattern (judge against fairness criteria)

- [ ] **`prompts/skill_gap_analyzer.py`** — Classify skill gaps with trainability
  - Input: `{rubric_json}`, `{cv_text}`, `{score_breakdown}`
  - Output: `SkillGapReport` (gaps list with: skill_name, gap_severity, trainability, evidence)
  - Key prompt technique: **Structured classification** (critical/trainable/non-critical)

- [ ] **`prompts/adaptive_scorer.py`** — Recalibrate score given bias/gaps/context
  - Input: `{original_score}`, `{bias_report}`, `{skill_gaps}`, `{reevaluation_reason}`
  - Output: `CandidateScore` (adjusted, with reasoning for adjustment)
  - Key prompt technique: **Constrained re-scoring** (can only adjust ±15%)

- [ ] **`prompts/supporter.py`** — Argue in favor of the candidate
  - Input: `{candidate_summary}`, `{score}`, `{skill_gaps}`
  - Output: structured argument (strengths, evidence, recommendation_for)

- [ ] **`prompts/critic.py`** — Argue against the candidate
  - Input: `{candidate_summary}`, `{score}`, `{skill_gaps}`
  - Output: structured argument (weaknesses, concerns, recommendation_against)

- [ ] **`prompts/decision_maker.py`** — Final arbitration between supporter & critic
  - Input: `{supporter_argument}`, `{critic_argument}`, `{score}`, `{bias_report}`
  - Output: `FinalDecision` (label: strong_fit/borderline/reject, reasoning, confidence)

- [ ] **`prompts/interview_generator.py`** — Generate targeted interview questions
  - Input: `{skill_gaps}`, `{candidate_summary}`, `{role_title}`
  - Output: list of `InterviewQuestion` (question, purpose, expected_signals, skill_targeted)

**🧪 Verification**: Print out each prompt with sample data filled in — does it read like a clear, effective instruction to an LLM?

---

### Step 1.3 — Upgrade Each Agent to Use Real LLM

> _Currently every agent (e.g., `jd_parser_agent.py`) uses hardcoded logic. Replace with LLM calls._

**Upgrade order** (follows the pipeline flow):

- [ ] **`agents/jd_parser_agent.py`** → `parse_jd_to_rubric(jd_text, role_title, level)`
  - Import prompt from `prompts/jd_parser.py`
  - Call `LLMClient.generate_structured()` with `JDRubric` schema
  - Remove all hardcoded `SkillRequirement` lists
  - Handle: what if LLM returns malformed JSON? → retry or fallback to basic rubric

- [ ] **`agents/cv_parser_agent.py`** → `parse_cv_to_structured_data(cv_text)`
  - Call LLM to extract full biographical and professional details
  - Ensure all dates, roles, and skills are extracted cleanly
  - Returns `ParsedCV` object

- [ ] **`agents/cv_scoring_agent.py`** → `score_candidate(candidate, rubric)`
  - Call LLM with CV text/parsed data + recruiter preferences (rubric)
  - Ensure `evidence_citations` point to real CV text spans
  - Include `confidence` score (0.0 - 1.0) in output

- [ ] **`agents/bias_detection_agent.py`** → `detect_bias(candidate, score)`
  - LLM analyzes the scoring rationale for bias proxies
  - Output `BiasReport` with `risk_level` (low/medium/high)

- [ ] **`agents/skill_gap_agent.py`** → `infer_skill_gaps(candidate, rubric)`
  - LLM classifies each required skill: present/missing/partial
  - Adds trainability assessment per gap

- [ ] **`agents/adaptive_scoring_agent.py`** → `adaptive_rescore(score, bias, skill_gaps)`
  - LLM recalibrates score considering bias flags and skill gap context
  - Score change constrained to ±15% of original

- [ ] **`agents/debate_agents.py`** → `run_supporter_critic_debate(cid, score, gaps)`
  - **Two separate LLM calls**: supporter then critic
  - Each receives the other's perspective (multi-turn: critic sees supporter argument)
  - Output `DebateRecord` with both arguments + `disagreement_score`

- [ ] **`agents/decision_agent.py`** → `decide_candidate(score, skill_gaps)`
  - LLM synthesizes all evidence into final `FinalDecision`
  - Labels: `strong_fit` / `borderline` / `reject` with reasoning

- [ ] **`agents/interview_question_agent.py`** → `generate_interview_questions(candidate, gaps)`
  - LLM generates 3-5 targeted questions based on identified skill gaps
  - Each question includes: purpose, expected signals, difficulty level

- [ ] **`agents/arbitration_agent.py`** → `should_rerun_evaluation(score, bias, debate)`
  - This can remain rule-based for now (not LLM):
    - Re-run if `confidence < 0.65`
    - Re-run if `bias.risk_level in ("medium", "high")`
    - Re-run if `debate.disagreement_score >= 0.65`

**🧪 Verification for each agent**:
```bash
# Test each agent independently with sample data
python -c "
from app.agents.jd_parser_agent import parse_jd_to_rubric
result = parse_jd_to_rubric('We need a Python developer with RAG experience...')
print(result.model_dump_json(indent=2))
"
```

### ✅ Stage 1 Complete When:
- [ ] Every agent makes a real LLM call (no more hardcoded responses)
- [ ] Every agent returns a valid Pydantic model
- [ ] Each agent can be called independently and produces reasonable output
- [ ] LLM errors are handled gracefully with retries and fallback

---

## 🟧 Stage 2: Deep Agent Orchestration — LangGraph + Feedback Loops (Days 5-8)

> **Goal**: Wire all agents into a real LangGraph `StateGraph` with conditional edges,
> feedback loops, and parallel execution. This is the **crown jewel** of the project.

### 🔗 Dependencies: Stage 1 complete (all agents working individually)

---

### Step 2.1 — Upgrade the State Model

> _Currently `models/state.py` has the basic TypedDict. Add loop tracking fields._

- [ ] **`models/state.py`** — Add deep agent loop tracking fields:
  ```python
  class HiringState(TypedDict, total=False):
      # ... existing fields ...
      
      # NEW: Loop tracking for deep agent behavior
      reevaluation_loops: int                      # How many times we've looped
      reevaluation_triggers: List[str]             # Audit trail: WHY each loop triggered
      per_candidate_loop_count: Dict[str, int]     # Per-candidate loop counts
      current_phase: str                           # Which node is currently executing
  ```

---

### Step 2.2 — Build the Real LangGraph StateGraph

> _Currently `langgraph_flow.py` defines node functions but NEVER compiles them into a StateGraph.
> `graph_runner.py` runs a plain Python while-loop instead. Fix both._

- [ ] **`services/langgraph_flow.py`** — Add graph compilation at the bottom:
  ```python
  from langgraph.graph import StateGraph, START, END
  
  graph = StateGraph(HiringState)
  
  # Add all nodes
  graph.add_node("jd_parser", jd_parser_node)
  graph.add_node("scorer", scorer_node)
  graph.add_node("bias_detector", bias_node)
  graph.add_node("skill_gap", skill_gap_node)
  graph.add_node("adaptive_scorer", adaptive_scoring_node)
  graph.add_node("debate", debate_node)
  graph.add_node("decision", decision_node)
  graph.add_node("interview", interview_node)
  
  # Linear edges (the pipeline flow)
  graph.add_edge(START, "jd_parser")
  graph.add_edge("jd_parser", "scorer")
  graph.add_edge("scorer", "bias_detector")
  graph.add_edge("bias_detector", "skill_gap")
  graph.add_edge("skill_gap", "adaptive_scorer")
  graph.add_edge("adaptive_scorer", "debate")
  
  # ★★★ DEEP AGENT CONDITIONAL EDGE ★★★
  # This is the feedback loop — the key differentiator
  graph.add_conditional_edges(
      "debate",
      should_reevaluate,   # Router function
      {
          "reevaluate": "bias_detector",   # Loop back to re-evaluate!
          "decide": "decision",            # Move forward to final decision
      }
  )
  
  graph.add_edge("decision", "interview")
  graph.add_edge("interview", END)
  
  # Compile the graph!
  compiled_graph = graph.compile()
  ```

---

### Step 2.3 — Build the Router Function (Deep Agent Logic)

- [ ] **In `services/langgraph_flow.py`** — Add the `should_reevaluate` function:
  ```python
  def should_reevaluate(state: HiringState) -> str:
      """Deep agent router: decides whether to loop back or move forward."""
      loop_count = state.get("reevaluation_loops", 0)
      
      # Safety: max 2 re-evaluation loops to prevent infinite cycles
      if loop_count >= 2:
          return "decide"
      
      triggers = []
      for cid, score in state["candidate_scores"].items():
          bias = state["bias_reports"].get(cid)
          debate = state["debate_records"].get(cid)
          
          if score.confidence < 0.65:
              triggers.append(f"{cid}: low confidence ({score.confidence})")
          if bias and bias.risk_level in ("medium", "high"):
              triggers.append(f"{cid}: bias risk ({bias.risk_level})")
          if debate and debate.disagreement_score >= 0.65:
              triggers.append(f"{cid}: high disagreement ({debate.disagreement_score})")
      
      if triggers:
          # Track WHY we're looping (audit trail)
          state["reevaluation_triggers"] = state.get("reevaluation_triggers", []) + triggers
          state["reevaluation_loops"] = loop_count + 1
          return "reevaluate"
      
      return "decide"
  ```

---

### Step 2.4 — Update Scorer Node for Parallel Execution

- [ ] **`services/langgraph_flow.py`** — Make `scorer_node` async with `asyncio.gather`:
  ```python
  async def scorer_node(state: HiringState) -> HiringState:
      rubric = state["rubric"]
      # Score ALL candidates in parallel
      tasks = [score_candidate(c, rubric) for c in state["candidates"]]
      results = await asyncio.gather(*tasks)
      state["candidate_scores"] = {
          r.candidate_id: r for r in results
      }
      return state
  ```

---

### Step 2.5 — Simplify graph_runner.py

- [ ] **`services/graph_runner.py`** — Replace the manual while-loop with compiled graph invocation:
  ```python
  from app.services.langgraph_flow import compiled_graph
  
  async def run_hiring_graph(job_id, jd_text, candidates):
      initial_state = {
          "job_id": job_id,
          "jd_text": jd_text,
          "candidates": candidates,
          "reevaluation_loops": 0,
          "reevaluation_triggers": [],
          "audit_log": [],
      }
      # The graph handles ALL orchestration now
      final_state = await compiled_graph.ainvoke(initial_state)
      return final_state
  ```

---

### Step 2.6 — Visualize the Graph

- [ ] Add a utility to generate the graph diagram:
  ```python
  # Run this to see your graph:
  from app.services.langgraph_flow import compiled_graph
  print(compiled_graph.get_graph().draw_mermaid())
  # Save as PNG:
  # compiled_graph.get_graph().draw_mermaid_png(output_file_path="docs/graph.png")
  ```

**🧪 Verification**:
```bash
# 1. Visualize the graph (should show the feedback loop)
python -c "from app.services.langgraph_flow import compiled_graph; print(compiled_graph.get_graph().draw_mermaid())"

# 2. Run the full pipeline with test data
python -c "
import asyncio
from app.services.graph_runner import run_hiring_graph
from app.models.schemas import CandidateProfile

candidates = [CandidateProfile(candidate_id='test-1', name='Test', cv_text='Python developer...')]
result = asyncio.run(run_hiring_graph('job-1', 'We need a Python dev...', candidates))
print('Loops triggered:', result.get('reevaluation_loops', 0))
print('Triggers:', result.get('reevaluation_triggers', []))
"
```

### ✅ Stage 2 Complete When:
- [ ] `compiled_graph.get_graph().draw_mermaid()` renders a graph with the feedback loop visible
- [ ] Pipeline runs end-to-end through the LangGraph (not through manual while-loops)
- [ ] Conditional edge triggers re-evaluation when confidence < 0.65 or bias is detected
- [ ] Loop caps at 2 iterations (no infinite loops)
- [ ] Audit log tracks which nodes executed and why re-evaluations triggered

---

## 🟦 Stage 3: Backend API + RAG System (Days 9-11)

> **Goal**: Build the real RAG pipeline (embeddings + vector store + reranker), wire up
> FastAPI endpoints, and add CV upload support.

### 🔗 Dependencies: Stage 2 complete (graph pipeline working end-to-end)

---

### Step 3.1 — Real Vector Store

- [ ] **`retrieval/vector_store.py`** — Replace placeholder with real ChromaDB:
  - Use `chromadb` with local persistent storage
  - Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (free, local)
  - Functions: `index_cv_chunks(candidate_id, chunks)`, `query_similar(query, top_k)`
  - Store metadata per chunk: `candidate_id`, `chunk_id`, `section`

---

### Step 3.2 — Real Hybrid Retrieval

- [ ] **`retrieval/hybrid.py`** — Replace proxy scores:
  - Real BM25 using `rank_bm25` library
  - Real vector similarity using ChromaDB embedding search
  - Reciprocal Rank Fusion (RRF) to merge BM25 + vector results
  - Output: list of `(chunk, rrf_score)` tuples

---

### Step 3.3 — Real Cross-Encoder Reranker

- [ ] **`retrieval/reranker.py`** — Replace token overlap:
  - Use `sentence-transformers` cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
  - Or Cohere Rerank API (free tier)
  - Rerank top-20 hybrid results → return top-5 with scores

---

### Step 3.4 — Enhanced Chunking

- [ ] **`retrieval/chunking.py`** — Improve the section-aware chunker:
  - Add 100-char overlap between chunks
  - Better section regex patterns (Education, Experience, Skills, Projects, etc.)
  - Attach metadata per chunk: section name, position index, detected skills

---

### Step 3.5 — CV Upload & PDF Parsing

- [ ] **`services/cv_parser.py`** — Real PDF extraction:
  - Use PyMuPDF (`fitz`) to extract text from uploaded PDFs
  - Clean extracted text (remove headers/footers, fix encoding)
  - Auto-chunk and index into vector store on upload

- [ ] **`main.py`** — Add new endpoints:
  - `POST /upload-cv` — upload PDF, extract text, chunk, index, return candidate_id
  - `POST /upload-jd` — upload job description text
  - `GET /candidates/{candidate_id}` — retrieve candidate profile
  - Ensure existing `POST /screen` endpoint uses the real graph pipeline

---

### Step 3.6 — Wire Evidence Service to Real RAG

- [ ] **`services/evidence_service.py`** — Connect to real retrieval:
  - On scoring, query vector store for relevant chunks per rubric requirement
  - Pass retrieved evidence to CV scoring agent
  - Track which chunks were cited in the final score

**🧪 Verification**:
```bash
# 1. Test vector store indexing and retrieval
python -c "
from app.retrieval.vector_store import VectorStore
vs = VectorStore()
vs.index_cv_chunks('test-1', [{'text': 'Python expert with 3 years...', 'section': 'Experience'}])
results = vs.query_similar('Python programming experience', top_k=3)
print(results)
"

# 2. Test PDF upload endpoint
curl -X POST http://localhost:8000/upload-cv \
  -F "file=@test_resume.pdf" \
  -F "candidate_name=Test User"

# 3. Run full pipeline through API
curl -X POST http://localhost:8000/screen \
  -H "Content-Type: application/json" \
  -d '{"job_id": "j1", "jd_text": "...", "candidates": [...]}'
```

### ✅ Stage 3 Complete When:
- [ ] Vector store indexes and retrieves CV chunks with real embeddings
- [ ] Hybrid retrieval (BM25 + vector) produces better results than either alone
- [ ] Reranker re-orders results with a cross-encoder
- [ ] PDF upload endpoint works end-to-end (upload → extract → chunk → index)
- [ ] `/screen` endpoint runs the full LangGraph pipeline and returns structured results
- [ ] Evidence citations in scores point to real CV text

---

## 🟪 Stage 4: Connect Frontend (Days 12-15)

> **Goal**: Build the React frontend that connects to your backend API and surfaces
> agent reasoning, scores, and the deep agent flow.

### 🔗 Dependencies: Stage 3 complete (backend serving data via API)

---

### Step 4.1 — API Integration Layer

- [ ] **`frontend-react/src/api/client.js`** — Create API client:
  - `uploadCV(file)` → `POST /upload-cv`
  - `submitJD(text)` → `POST /upload-jd`
  - `screenCandidates(jobId, jdText, candidates)` → `POST /screen`
  - `getCandidateResults(candidateId)` → `GET /candidates/{id}`
  - Error handling, loading states

---

### Step 4.2 — Recruiter Dashboard

- [ ] **`frontend-react/src/components/RecruiterDashboard.jsx`**:
  - Job posting form (paste JD, preview generated rubric)
  - CV upload area (drag & drop, multi-file)
  - "Run Screening" button → triggers `/screen` endpoint
  - Loading state with progress indicator

---

### Step 4.3 — Shortlist Table

- [ ] **`frontend-react/src/components/ShortlistTable.jsx`**:
  - Ranked table of candidates with: name, score, confidence, label, evidence count
  - Color coding: green (strong_fit), yellow (borderline), red (reject)
  - Sortable columns
  - Click row → expand to candidate detail

---

### Step 4.4 — Candidate Deep Dive Panel

- [ ] **`frontend-react/src/components/CandidateDeepDive.jsx`**:
  - Score breakdown with per-skill scores + evidence citations
  - Bias flags and mitigation actions
  - Skill gap matrix (critical / trainable / non-critical)
  - Debate transcript (supporter vs critic arguments side by side)
  - Final decision reasoning
  - Generated interview questions

---

### Step 4.5 — Agent Flow Visualization

- [ ] **`frontend-react/src/components/AgentFlowDiagram.jsx`**:
  - Visual representation of LangGraph execution
  - Highlight which nodes executed, which feedback loops triggered
  - Show latency per node
  - Confidence gauges per decision point
  - **This is the "wow factor" — visualizing the deep agent reasoning**

---

### Step 4.6 — Candidate Self-Service Panel (Optional)

- [ ] **`frontend-react/src/components/CandidatePanel.jsx`**:
  - Upload CV against a specific role
  - View fit probability + mismatch reasons
  - Improvement suggestions
  - What-if: re-upload updated CV, compare scores

**🧪 Verification**:
```bash
# 1. Start backend
cd backend && uvicorn app.main:app --reload

# 2. Start frontend
cd frontend-react && npm run dev

# 3. Test the full flow in browser:
#    - Paste a JD → see rubric generated
#    - Upload a CV → see it processed
#    - Click "Screen" → see ranked results
#    - Click a candidate → see full deep dive with agent reasoning
```

### ✅ Stage 4 Complete When:
- [ ] JD input → rubric preview works in the UI
- [ ] CV upload → processing → results displayed in ranked table
- [ ] Candidate deep dive shows all agent outputs (scores, bias, gaps, debate, decision)
- [ ] Agent flow diagram visualizes which nodes ran and which loops triggered
- [ ] The whole flow works end-to-end: frontend → API → graph → LLM → response → rendered

---

## ✨ Stage 5: Polish, Evaluate & Harden (Days 16-21)

> **Goal**: Make it production-grade and interview-ready with evaluation, reliability, and observability.

### 🔗 Dependencies: Stage 4 complete (full stack working)

---

### Step 5.1 — Evaluation Harness

- [ ] Create `tests/evals/golden_data/hiring_scenarios.json` — 10-15 JD/CV pairs with expected labels
- [ ] Build `tests/evals/eval_runner.py` — Run golden dataset through pipeline, measure:
  - `Precision@K` for shortlist quality
  - `NDCG` for ranking accuracy
  - `citation_faithfulness` — are evidence quotes real?
  - `decision_label_accuracy` — predicted vs golden label match rate
- [ ] Build `tests/evals/test_regression.py` — Run eval suite, fail CI if metrics drop

### Step 5.2 — Unit Tests

- [ ] `tests/unit/test_chunking.py` — Chunking correctness
- [ ] `tests/unit/test_retrieval.py` — Retrieval returns relevant chunks
- [ ] `tests/unit/test_agents.py` — Each agent returns valid Pydantic output
- [ ] `tests/unit/test_state.py` — State transitions via LangGraph are valid

### Step 5.3 — Reliability Hardening

- [ ] Circuit breaker: after 3 LLM failures → fall back to rule-based scoring
- [ ] Timeout per candidate end-to-end: 120s max
- [ ] Idempotent processing: same CV upload doesn't reprocess
- [ ] PII redaction in logs (mask candidate names/emails)

### Step 5.4 — Observability

- [ ] Per-agent latency tracking in structured logs
- [ ] Cost-per-candidate calculation (total tokens × price)
- [ ] LangSmith traces for every pipeline run (already partially wired)

### Step 5.5 — CI/CD

- [ ] `.github/workflows/ci.yml` — Lint (ruff), type check (mypy), unit tests, eval regression
- [ ] Block merge if any quality gate fails

### ✅ Stage 5 Complete When:
- [ ] Golden dataset evaluation produces measurable metrics
- [ ] All unit tests pass
- [ ] System gracefully handles LLM failures
- [ ] LangSmith traces capture every pipeline run
- [ ] CI pipeline runs on every push

---

## 🎯 Quick Reference — File Change Map

| Stage | Files to CREATE | Files to MODIFY |
|-------|----------------|-----------------|
| **1** | `.env` | `core/llm.py`, `core/config.py`, all `prompts/*.py`, all `agents/*.py` |
| **2** | — | `models/state.py`, `services/langgraph_flow.py`, `services/graph_runner.py` |
| **3** | `services/cv_parser.py` (expand) | `retrieval/vector_store.py`, `retrieval/hybrid.py`, `retrieval/reranker.py`, `retrieval/chunking.py`, `services/evidence_service.py`, `main.py` |
| **4** | `frontend-react/src/api/client.js`, multiple `components/*.jsx` | `frontend-react/src/App.jsx` |
| **5** | `tests/evals/*`, `tests/unit/*`, `.github/workflows/ci.yml` | Various (hardening) |

---

## 💡 Tips Before You Start

1. **Test each agent in isolation BEFORE wiring into the graph** — debugging a 9-node pipeline is 10× harder than debugging one node
2. **Use `gpt-4o-mini` during development** (cheap + fast) — switch to `gpt-4o` only for eval/production
3. **Keep LangSmith tracing on** — you'll want to see exactly what prompts went in and what came out
4. **Commit after each step** — not after each stage. Smaller commits = easier debugging
5. **The feedback loop is the star** — spend extra time getting `should_reevaluate()` right

---

> **Ready to start?** Begin with **Stage 1, Step 1.1** — building `core/llm.py`.
> Everything else flows from having a working LLM client.
