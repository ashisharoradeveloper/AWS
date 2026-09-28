# Roadmap

The roadmap is deliberately incremental. Each phase should leave the project runnable and testable locally.

## Phase 0: project foundation

- Confirm CSV rules, authentication/session choice, file limits, retention, and output behavior.
- Create backend and frontend skeletons.
- Add repository configuration, environment examples, formatting, linting, and test runners.
- Add a minimal health endpoint and a frontend shell.

## Phase 1: first vertical slice

Implemented first milestone: a local, unauthenticated CSV analysis slice behind a narrow backend API and Dockerized React client.

- Accept one bounded CSV upload.
- Validate the file and parse a header row.
- Calculate a small, documented summary such as total rows, missing values, and numeric min/max.
- Return the summary synchronously.
- Add unit tests for valid input, malformed input, empty input, and oversized input.
- Add one API test for upload and response behavior.
- Render the result in a minimal React screen.

This milestone intentionally excludes accounts, durable storage, background workers, downloads, and AWS. It tests the core learning path and CSV rules before authentication and persistence multiply the number of moving parts.

## Phase 2: persistence and file ownership

- Add PostgreSQL and SQLAlchemy models/migrations.
- Store file metadata and processing records.
- Add local file storage behind a small storage abstraction.
- Introduce explicit processing status and failure records.
- Add authenticated ownership checks once the account model is specified.

## Phase 3: authentication and complete MVP workflow

- Add registration, login, logout/session expiry, and authorization.
- Add upload history, status polling, results pages, and secure downloads.
- Add duplicate detection and the agreed validation/statistics policy.
- Add retention and deletion behavior.
- Add security and integration tests for cross-user access.

## Phase 4: asynchronous processing and observability

Move processing to a worker only when file sizes, processing duration, concurrency, or user experience justify it.

- Define a job contract and retry/idempotency behavior.
- Introduce a queue and worker locally first.
- Add structured logs, metrics, tracing, and correlation IDs.
- Make status transitions and failure recovery observable.

## Phase 5: EC2 deployment learning

- Assign an Elastic IP to keep the EC2 public address stable.
- Run the existing frontend and backend containers on a private Docker network.
- Add an Nginx gateway as the sole public entry point, routing `/api/` to FastAPI and other paths to the frontend.
- Validate health and CSV upload over the single public origin; expose port 80 rather than the application ports.
- Replace the Vite development server with a production frontend build before treating this as production deployment.

## Phase 6: AWS evolution

Adopt managed AWS components one at a time, preserving the application contracts:

- S3 for durable object storage and downloads.
- RDS for managed PostgreSQL.
- SQS plus a worker runtime for asynchronous processing.
- CloudWatch for logs, metrics, and alarms.
- Secrets Manager or Parameter Store for runtime secrets/configuration.
- A managed identity provider only if application-managed authentication becomes an operational burden.

Each adoption should include a reason, cost/complexity review, rollback or local-development story, and updated architecture documentation.
