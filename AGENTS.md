# AWS File Processing Lab: AI Project Context

## Purpose

This is a learning project for building a small CSV file-processing web application while learning Python/FastAPI, React/TypeScript, PostgreSQL, Docker, AWS, asynchronous processing, observability, and spec-driven development.

## Current state

Phase 1 is implemented as a Dockerized, unauthenticated CSV analysis slice. It includes a FastAPI backend, a React/Vite frontend, focused backend tests, and Docker Compose. Do not add authentication, PostgreSQL, persistence, workers, downloads, or AWS resources until the next milestone is explicitly requested.

## Architecture

Start with a modular monolith:

```text
React/Vite -> FastAPI -> PostgreSQL
                         -> local file storage
```

CSV processing starts synchronously for bounded files. The design may later evolve to S3, SQS, a worker, RDS, and managed observability, but AWS services must be introduced only when a documented requirement justifies them.

## Technology stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL, pytest.
- Frontend: React, TypeScript, Vite.
- Local development: Docker and Docker Compose.
- Cloud: AWS introduced incrementally; no default assumption of Kubernetes, ECS, EKS, Lambda, Kafka, Redis, or SQS.

## Repository structure

- `backend/`: FastAPI application and backend tests.
- `frontend/`: React/Vite application and frontend tests.
- `docs/`: requirements, architecture, development workflow, and roadmap.
- `docker/`: Docker support when local services require it.
- `storage/`: runtime-only local files; never commit uploaded data.

## Engineering conventions

- Follow spec-driven development: understand, specify, design, identify trade-offs, implement, test, review, and document.
- Keep changes small and vertically testable.
- Prefer clear modules over premature microservices or abstractions.
- Validate untrusted input on the server and enforce upload limits.
- Enforce user ownership on every file, result, and download operation.
- Never log passwords, secrets, or raw uploaded content.
- Hash passwords with a proven library; never store plaintext passwords.
- Use migrations for schema changes and tests for behavior changes.
- Keep API contracts and processing rules documented.
- Do not silently make meaningful architectural decisions. Explain options and recommendation in the relevant document first.

## Running and testing

From the repository root, use `docker compose build`, then `docker compose up`. The frontend runs at `http://localhost:5173` and the API at `http://localhost:8000`. Run backend tests with `docker compose run --rm backend pytest` and build the frontend with `docker compose run --rm frontend npm run build`. See `docs/development.md` for the current workflow. Use a committed `.env.example` when environment configuration is introduced and keep real secrets out of source control.

## Decision rules

- First implementation milestone: a local synchronous CSV analysis vertical slice with focused unit/API tests.
- Add PostgreSQL and durable metadata after CSV behavior is understood.
- Add authentication before exposing user-owned history or downloads.
- Add background processing only when file size, duration, concurrency, or user experience makes synchronous work insufficient.
- Add AWS services individually with a documented problem, benefit, complexity cost, and adoption threshold.

Read `docs/requirements.md`, `docs/architecture.md`, `docs/development.md`, and `docs/roadmap.md` before making changes that affect scope or architecture.
