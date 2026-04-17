# Project 08 - AI Hiring Screener (Deep Agent System)

Production-focused hiring intelligence system built with LangChain and LangGraph.

## What this project implements

- Recruiter panel: create jobs, upload CVs, review ranked candidates.
- Candidate panel: self-check fit probability and mismatch reasons.
- Deep-agent workflow: scoring, bias checks, adaptive rescoring, debate, final decision.
- Hybrid RAG: BM25 + vector retrieval with reranking.
- Interview-ready engineering: evaluations, observability, reliability, and security controls.

## Core stack

- Python, FastAPI, Pydantic
- LangChain, LangGraph
- Chroma + BM25 + cross-encoder rerank (pluggable)
- PyMuPDF for CV parsing
- React (Vite) frontend

## Virtual environments

Created environments:

- Backend venv: `backend/.venv`
- Frontend venv: `frontend-react/.venv`

Activate backend venv:

- `cd "/Users/sahilsoni/Desktop/project8-deep-agents/backend"`
- `source .venv/bin/activate`

Activate frontend venv:

- `cd "/Users/sahilsoni/Desktop/project8-deep-agents/frontend-react"`
- `source .venv/bin/activate`

## Run order (implementation roadmap)

1. Product scope + schemas
2. Hybrid retrieval
3. Agent graph (v1)
4. Deep-agent layer
5. Recruiter + candidate UX
6. Evals + hardening

## Note

This repo is scaffolded to match an industry-ready junior AI engineer portfolio project.

## Frontend

## Run backend (FastAPI)

1. `cd "/Users/sahilsoni/Desktop/project8-deep-agents/backend"`
2. `source .venv/bin/activate`
3. `pip install -e .`
4. `uvicorn app.main:app --reload`

## Run frontend (React)

1. `cd "/Users/sahilsoni/Desktop/project8-deep-agents/frontend-react"`
2. `source .venv/bin/activate`
3. `cp .env.example .env`
4. `npm install`
5. `npm run dev`
