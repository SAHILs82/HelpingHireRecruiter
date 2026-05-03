# 🚀 HelpHire — AI-Powered Recruitment Platform

> **The Smartest Way to Hire & Get Hired**

HelpHire is a full-stack, AI-powered recruitment platform that automates the entire hiring pipeline — from writing job descriptions to scoring candidates — using a multi-agent architecture with domain-specific intelligence.

---

## ✨ Key Features

### 🧠 Intelligent JD Generation
- Recruiter fills a minimal intake form (domain + short description)
- AI generates a **production-ready Job Description** with industry-standard requirements, skills, and responsibilities
- Domain-specific prompts ensure the output reflects real-world standards (e.g., CI/CD for Software Engineers, HIPAA for Healthcare)

### 📄 Automated CV Parsing
- Candidates upload their resume (PDF)
- **PyMuPDF** extracts raw text from multi-format, multi-column layouts
- A **LangChain agent** reconstructs the noisy text into a structured candidate profile (skills, experience, education, projects)
- Parsed data is validated via **Pydantic models** and stored in PostgreSQL

### ⚡ AI-Powered CV Scoring
- Candidates are scored against the JD using a **weighted evaluation rubric**:
  - Skills (45%) · Experience (25%) · Projects (20%) · Education (10%)
- **Mathematical verification** independently recalculates the weighted score to catch LLM hallucinations
- Scores are stored with full reasoning and evidence for transparency

### 🎯 Dynamic Prompt Orchestration
- Replaced a single generic AI instruction with **18 domain-specialized prompts** across Technical, Non-Technical, and Industry verticals
- An **intelligent Domain Mapper** auto-routes recruiter inputs to the correct specialized prompt using regex-based semantic matching
- Prompts are stored in a **database-driven management system** — hot-swappable at runtime without code redeployment

### 👥 Dual-Portal Architecture
- **Recruiter Portal:** Create JDs, manage intakes, view candidate leaderboards, trigger AI scoring
- **Job Seeker Portal:** Browse open positions, upload CVs, track application status

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  JD Intake   │  │  Job Seeker  │  │  Scoring Leaderboard    │ │
│  │  Form        │  │  Dashboard   │  │  & Candidate Profiles   │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬────────────┘ │
└─────────┼────────────────┼───────────────────────┼──────────────┘
          │                │                       │
          ▼                ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                    │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │  JD Intake  │  │ CV Parsing │  │ CV Scoring │  │   Jobs    │ │
│  │  API        │  │ API        │  │ API        │  │   API     │ │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘ │
│        │               │               │               │       │
│        ▼               ▼               ▼               │       │
│  ┌──────────────────────────────────────────────┐      │       │
│  │          AI AGENT LAYER (LangChain)          │      │       │
│  │                                              │      │       │
│  │  ┌──────────────┐  ┌───────────────────────┐ │      │       │
│  │  │ Domain Mapper │  │  Dynamic LLM Prompts  │ │      │       │
│  │  │ (Auto-Route)  │  │  (DB-Driven, 54 seed) │ │      │       │
│  │  └──────┬───────┘  └───────────┬───────────┘ │      │       │
│  │         │                      │              │      │       │
│  │         ▼                      ▼              │      │       │
│  │  ┌─────────────┐  ┌──────────────────────┐   │      │       │
│  │  │ JD Generator │  │ CV Parser  │ Scorer  │   │      │       │
│  │  │ Agent        │  │ Agent      │ Agent   │   │      │       │
│  │  └─────────────┘  └──────────────────────┘   │      │       │
│  └──────────────────────────────────────────────┘      │       │
│        │               │               │               │       │
│        ▼               ▼               ▼               ▼       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL (Data Layer)                      │   │
│  │  Jobs · Candidates · Scores · Applications · Prompts     │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy |
| **AI/ML** | LangChain, LangGraph, OpenAI/NVIDIA/OpenRouter LLMs |
| **CV Parsing** | PyMuPDF (fitz) |
| **Database** | PostgreSQL |
| **Observability** | LangSmith Tracing |
| **DevOps** | Docker Compose |

---

## 📂 Project Structure

```
helphire/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── agents/          # LangChain-powered AI agents
│   │   │   ├── prompts/         # Fallback prompt templates
│   │   │   ├── schema/          # Pydantic models for structured LLM output
│   │   │   ├── services/        # Business logic (prompt prep, scoring, storage)
│   │   │   └── utils/           # Domain mapper, helpers
│   │   ├── api/                 # FastAPI route handlers
│   │   ├── db/models/           # SQLAlchemy ORM models
│   │   ├── schemas/             # Request/Response Pydantic schemas
│   │   ├── services/            # Core services (CV parser, etc.)
│   │   └── state/               # Agent state definitions
│   └── scripts/
│       └── seed_prompts.py      # Seeds 54 domain-specific prompts to DB
│
├── frontend-react/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── api/             # API client functions
│   │   │   └── ui/              # ShadCN-style UI primitives
│   │   ├── pages/               # Route pages (JD Intake, Scoring, etc.)
│   │   └── App.jsx              # Root with routing
│   └── vite.config.js
│
├── docker-compose.yml           # PostgreSQL service
└── README.md
```

---

## 🧩 Domain-Specific Intelligence

The platform supports **18 specialized domains**, each with tailored evaluation metrics, industry frameworks, and scoring priorities:

| Category | Domains |
|----------|---------|
| **Technical** | Software Engineer · Data Science · DevOps/Cloud · Product Manager · UI/UX Designer · Cyber Security |
| **Non-Technical** | Sales · Marketing · HR/People Ops · Finance/Accounts · Operations · Customer Support |
| **Industry-Specific** | Healthcare · Legal · Education · Manufacturing · Retail/E-Commerce · Media/Creative |

Each domain has **3 specialized prompts** (JD Generator, CV Scorer, JD Parser) = **54 total prompts** seeded into the database.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Start the Database
```bash
docker-compose up -d
```

### 2. Run the Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

### 3. Seed Domain Prompts
```bash
cd backend
python -m scripts.seed_prompts
```

### 4. Run the Frontend
```bash
cd frontend-react
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

---

## 🗺️ Roadmap

- [x] JD Intake & AI-Powered JD Generation
- [x] CV Upload & Automated Parsing (PyMuPDF + LangChain)
- [x] Weighted CV Scoring with Hallucination Verification
- [x] Domain-Specific Prompt Library (54 prompts across 18 domains)
- [x] Intelligent Domain Mapper (Auto-routing)
- [x] Database-Driven Dynamic Prompt Management
- [x] LangSmith Tracing for Observability
- [x] Dual-Portal (Recruiter + Job Seeker)
- [ ] Deep Agent — LangGraph Human-in-the-Loop with planning, approval, and feedback loops
- [ ] RAG Pipeline — Retrieval-Augmented Generation for richer candidate-JD matching
- [ ] Bias Detection & Adaptive Rescoring
- [ ] Multi-Agent Debate System for candidate evaluation
- [ ] Interview Question Generation based on skill gaps

---

## 📄 License

This project is built for educational and portfolio purposes.

---

<p align="center">
  Built with ❤️ by <strong>Sahil Soni</strong>
</p>
