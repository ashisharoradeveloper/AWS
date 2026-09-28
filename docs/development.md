# Development Guide

## Current status

Phase 1 is implemented as a small Dockerized vertical slice. It provides a FastAPI CSV analysis API and a React/Vite upload interface. It does not include authentication, PostgreSQL, persistence, background processing, downloads, or AWS resources yet.

## Planned local prerequisites

The first implementation milestone is expected to use:

- Python 3.12 or the version selected and pinned by the project.
- Node.js LTS and npm.
- Docker Desktop with Docker Compose.
- Git.

Exact versions should be pinned when the first backend and frontend projects are created.

## Local services

The current Docker Compose topology is:

- FastAPI backend.
- React/Vite frontend.
- No database or file-storage service yet; uploads are analyzed in memory and discarded after the response.

PostgreSQL and persistent local storage belong to the next milestone. They are not represented by placeholder containers.

## Commands

From the repository root:

```shell
# Build the backend and frontend images.
docker compose build

# Start both development services.
docker compose up

# Backend tests inside the pinned Python container.
docker compose run --rm backend pytest

# Frontend type-check and production build inside the Node container.
docker compose run --rm frontend npm run build
```

The frontend is available at `http://localhost:5173`. The API is available at `http://localhost:8000`, with a health check at `/api/v1/health` and CSV analysis at `/api/v1/analyze`.

The backend container mounts `backend/app` for quick code iteration. The frontend container mounts the source tree and keeps `node_modules` in a Docker volume.

## EC2 direct-Docker learning deployment

This deployment uses the existing Docker images without Compose. Nginx is the only container publishing a host port; the frontend and backend communicate with it over a user-defined Docker network. The browser and API share one origin, so the frontend uses a relative `/api/` URL.

From the repository root on EC2, build the images:

```shell
docker build -t aws-backend ./backend
docker build -t aws-frontend ./frontend
docker network inspect aws-lab >/dev/null 2>&1 || docker network create aws-lab
```

Replace the existing app containers with network-only containers, then start the gateway:

```shell
docker rm -f aws-gateway aws-frontend aws-backend 2>/dev/null || true
docker run -d --name aws-backend --network aws-lab --restart unless-stopped aws-backend
docker run -d --name aws-frontend --network aws-lab --restart unless-stopped \
	-e VITE_API_URL= aws-frontend
docker run -d --name aws-gateway --network aws-lab --restart unless-stopped \
	-p 80:80 \
	-v "$HOME/AWS/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
	nginx:alpine
```

The `docker rm -f` command replaces containers with these names, so it causes a brief outage. Allow inbound TCP port 80 in the EC2 security group. After testing the app through the Elastic IP, port 5173 and 8000 no longer need public inbound rules. The current frontend image runs Vite's development server; use a production static build before exposing this as a production service.

Verify on EC2 with `curl http://localhost/` and `curl http://localhost/api/v1/health`, then open `http://<elastic-ip>/` from a browser and upload a CSV.

## Configuration and secrets

Use environment variables for database URLs, secret keys, storage roots, upload limits, and runtime configuration as those features are introduced. Provide a safe example configuration file such as `.env.example`; never commit real credentials. The current frontend uses `VITE_API_URL`, defaulting to `http://localhost:8000`.

## Testing approach

- Unit-test CSV parsing, validation, duplicate detection, statistics, and state transitions without a database or network.
- API-test authentication, ownership checks, upload validation, status, results, and download behavior.
- Add frontend tests for important user workflows and error states.
- Use an isolated test database or transaction strategy for database integration tests.
- Add an end-to-end smoke test only after the core API and UI workflows exist.

## Implementation workflow

For each milestone:

1. Update the relevant specification and make assumptions explicit.
2. Implement the smallest vertical slice.
3. Add focused tests before broad refactoring.
4. Run formatting, linting, type checking, and tests.
5. Review security and ownership boundaries.
6. Update documentation and record architectural decisions.

Do not combine unrelated features into one milestone. Keep database migrations versioned and review schema changes as part of the API contract.
