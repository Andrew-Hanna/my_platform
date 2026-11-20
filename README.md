# LMS

A learning management platform for live sessions, recordings, booklets, and assessments.

## Layout

- `backend/` — FastAPI API (Python 3.12). See `backend/app/`.
- `frontend/` — React + TypeScript app (Vite).
- `docs/` — architecture, data model, flows, decisions, and milestone checklists.
- `PROJECT_PLAN.md` — features, user stories, and decisions.
- `TASKS.md` — phased task list with the definition of done.

## Run locally

1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD` if you change it.
2. Start the database: `docker compose up -d db`
3. Backend: `cd backend && uv sync && uv run uvicorn app.main:app --reload`
4. Tests: `cd backend && uv run pytest`

Architecture rules are in `docs/architecture.md`.
