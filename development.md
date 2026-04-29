# Development guide

This document explains the commands you use day to day: what they do, when to run them, and in what order.

## Prerequisites

- **Python 3.11+** (backend)
- **Node.js** and **npm** (frontend)
- **Docker** (optional but recommended for PostgreSQL)

---

## Repository layout (short)

| Path | Role |
|------|------|
| `backend/` | FastAPI app (`app/`), SQLAlchemy, Alembic migrations |
| `frontend-react/` | Vite + React UI |
| `tests/` | Pytest suite (run from repo root) |
| `docker-compose.yml` | Local PostgreSQL service |

---

## 1. PostgreSQL (database)

The app expects a PostgreSQL URL in `backend/.env` as `DATABASE_URL` (see `backend/.env.example`). Docker Compose creates a matching database for local development.

### Start Postgres in the background

```bash
docker compose up -d postgres
```

- **`docker compose`**: reads `docker-compose.yml` in the current directory and runs the defined services.
- **`up`**: create and start containers.
- **`-d`**: detached mode (runs in the background so your terminal stays free).

### See container status

```bash
docker compose ps
```

### View Postgres logs (if something fails)

```bash
docker compose logs -f postgres
```

- **`-f`**: follow new log lines (Ctrl+C to stop following).

### Stop Postgres (keeps data in the named volume)

```bash
docker compose stop postgres
```

### Stop and remove containers (data volume is kept unless you add `-v`)

```bash
docker compose down
```

### Reset the database completely (deletes the Docker volume — **all local DB data is lost**)

```bash
docker compose down -v
```

Then start again with `docker compose up -d postgres` and run migrations (below).

---

## 2. Backend (FastAPI)

All backend commands below assume your shell’s current directory is **`backend/`**:

```bash
cd backend
```

### Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

- Creates a folder `.venv` with an isolated Python environment.

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows (PowerShell):**

```bash
.\.venv\Scripts\Activate.ps1
```

After activation, `python` and `pip` refer to this venv.

### Install the backend package and dependencies

```bash
pip install -e .
```

- **`pip install`**: installs packages.
- **`-e .`**: editable install of the project in the current directory (`backend/`), so code changes are picked up without reinstalling.

### Environment variables

Copy the example file and edit secrets as needed:

```bash
cp .env.example .env
```

- **`cp`**: copies `.env.example` to `.env` (the app loads `.env` via Pydantic settings; do not commit real secrets).

Important keys include `DATABASE_URL`, `OPENAI_API_KEY`, and optional LangSmith settings.

### Database migrations (Alembic)

Run these **after** Postgres is up and `DATABASE_URL` in `.env` is correct.

Apply all pending migrations (creates/updates tables such as `jobs`):

```bash
alembic upgrade head
```

- **`alembic`**: migration tool configured by `alembic.ini` and `alembic/`.
- **`upgrade`**: move the database schema forward.
- **`head`**: latest revision in `alembic/versions/`.

Show current migration revision:

```bash
alembic current
```

Revert one migration step (use with care):

```bash
alembic downgrade -1
```

Alembic reads **`DATABASE_URL`** from the environment. If it is not set, load `.env` first, for example:

```bash
set -a && source .env && set +a && alembic upgrade head
```

(macOS/Linux: `set -a` exports variables from the sourced file so child processes like Alembic see them.)

### Run the API server (development)

```bash
uvicorn app.main:app --reload
```source .venv/bin/activate


- **`uvicorn`**: ASGI server that runs FastAPI.
- **`app.main:app`**: module `app.main`, variable `app` (the `FastAPI()` instance).
- **`--reload`**: restart the process when Python files change (development only).

Default URL: **http://127.0.0.1:8000** — OpenAPI docs: **http://127.0.0.1:8000/docs**

---

## 3. Frontend (React + Vite)

From the repo root:

```bash
cd frontend-react
```

### Install JavaScript dependencies

```bash
npm install
```

- Reads `package.json` and downloads packages into `node_modules/`.

### Environment file (if the app needs API URLs, etc.)

```bash
cp .env.example .env
```

Edit `.env` if your backend URL is not the default.

### Dev server with hot reload

```bash
npm run dev
```

- **`npm run`**: runs a script from `package.json` under `"scripts"`.
- **`dev`**: in this project starts **Vite** for local development.

### Production-style build

```bash
npm run build
```

### Lint JavaScript/JSX

```bash
npm run lint
```

### Preview the production build locally

```bash
npm run preview
```

---

## 4. Tests (pytest)

Run from the **repository root** (not `backend/`), because `pytest.ini` sets `pythonpath = backend`:

```bash
cd /path/to/project8-deep-agents
pytest
```

Quiet output:

```bash
pytest -q
```

Run a single file:

```bash
pytest tests/integration/test_screening.py
```

---

## 5. Setup progress: steps 1–3 done, what to run next

If you already finished **through installing the backend** (Postgres in Docker, Python venv, `pip install -e .`), continue from **step 4** below.

### Steps 1–3 (already done — recap only)

| Step | What you ran |
|------|----------------|
| 1 | From repo root: `docker compose up -d postgres` |
| 2 | `cd backend`, create venv, `source .venv/bin/activate` (see §2) |
| 3 | Still in `backend/` with venv active: `pip install -e .` |

### Step 4 — Environment file (do this once, or when keys change)

Stay in **`backend/`** with the venv **activated**:

```bash
cd backend
source .venv/bin/activate
cp .env.example .env
```

Edit **`backend/.env`** in your editor:

- **`DATABASE_URL`** should match Docker (default in `.env.example` is fine if you did not change Compose):
  - `postgresql+asyncpg://project8:project8@127.0.0.1:5432/HelpingHireRecruiter`
- Set **`OPENAI_API_KEY`** when you call the LLM from the app.
- Optional: LangSmith keys if you use tracing.

### Step 5 — Apply database migrations (Alembic)

Postgres must be running (`docker compose ps`). Load `.env` so Alembic sees `DATABASE_URL`, then upgrade:

```bash
cd backend
source .venv/bin/activate
set -a && source .env && set +a && alembic upgrade head
```

- **`set -a`**: every variable defined while sourcing `.env` is exported (Alembic’s process inherits `DATABASE_URL`).
- **`alembic upgrade head`**: applies all migrations (e.g. creates the `jobs` table).

Check that the revision applied:

```bash
set -a && source .env && set +a && alembic current
```

You should see revision **`0001`** (or whatever is latest under `backend/alembic/versions/`).

### Step 6 — Run the API

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

- Open **http://127.0.0.1:8000/docs** for Swagger UI.

### Step 7 — Frontend (separate terminal)

From the **repository root** (parent of `backend/`):

```bash
cd frontend-react
cp .env.example .env
npm install
npm run dev
```

- Vite prints a local URL (often **http://127.0.0.1:5173**).

### Every new terminal session (backend)

Before `uvicorn` or `alembic`, always:

```bash
cd backend
source .venv/bin/activate
```

---

## 6. Full “first time” order (reference)

1. `docker compose up -d postgres`
2. `cd backend && python -m venv .venv && source .venv/bin/activate` (Windows: use `.\.venv\Scripts\Activate.ps1`)
3. `pip install -e .`
4. `cp .env.example .env` — edit `DATABASE_URL` and API keys
5. `set -a && source .env && set +a && alembic upgrade head`
6. `uvicorn app.main:app --reload`
7. New terminal: `cd frontend-react && cp .env.example .env && npm install && npm run dev`

---

## 7. Quick reference

| Goal | Command |
|------|---------|
| Start DB | `docker compose up -d postgres` (repo root) |
| Backend deps (once) | `cd backend && source .venv/bin/activate && pip install -e .` |
| **After step 3 — load env + migrate** | `cd backend && source .venv/bin/activate && set -a && source .env && set +a && alembic upgrade head` |
| Run API | `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload` |
| Run UI | `cd frontend-react && npm run dev` |
| Run tests | `pytest` (from repo root) |

If a command fails, check that Postgres is healthy (`docker compose ps`), `DATABASE_URL` matches Docker (`user`, `password`, database name `HelpingHireRecruiter`), and that you activated the backend virtual environment before `pip` / `uvicorn` / `alembic`.
