# Phase 0 — Project setup

## Checklist
- [x] S0.1 Folders backend/, frontend/, docs/ and README.md
- [x] S0.2 Backend project with uv; FastAPI and uvicorn installed
- [x] S0.3 GET /health with pytest tests (5 tests in backend/tests, see notes)
- [x] S0.4 docker-compose.yml with PostgreSQL 16 — database started with `docker compose up -d db`
- [x] S0.5 Settings from environment; .env.example; .gitignore ignores .env
- [x] S0.6 SQLAlchemy base and Alembic configured; `alembic upgrade head` runs against PostgreSQL (no migrations yet)
- [x] S0.7 Vite + React + TypeScript frontend
- [x] S0.8 Frontend calls /api/health through the Vite proxy
- [x] S0.9 Lint and format: ruff (backend); oxlint and Prettier (frontend). ESLint was replaced by oxlint, the default from the Vite template.
- [x] S0.10 .gitignore for Python, Node, .env, uploads
- [x] S0.11 GitHub Actions workflow (.github/workflows/ci.yml)
- [x] S0.12 docs/architecture.md with layer rules and folder map
- [x] S0.13 Architecture diagram (Mermaid) in docs/architecture.md

## Test results
- Backend: `uv run pytest -q` → 5 passed
- Backend lint: `uv run ruff check` → passed; `ruff format --check` → passed after formatting
- Frontend: `npm run lint` → exit 0; `npm run build` → passed
- Live check: backend on port 8000 returned `{"status":"ok"}` for GET /health
- Database: `docker compose up -d db` started PostgreSQL 16; `alembic upgrade head` ran without error

## Notes and deviations
- **Test-first not followed for Phase 0.** The test agent was started while the build was in progress, so the 5 backend tests were never seen failing before the code existed. They pass against the current code. Phase 1 onward should write tests first, as TASKS.md requires.
- **Docker Compose not run.** The file is written, but the database was not started in this run, so the Alembic migration step has not been run against PostgreSQL.
- **Lint tool:** oxlint instead of ESLint, which the Vite template provides.
- **CI not run** on GitHub yet; the workflow has been written but not pushed.
