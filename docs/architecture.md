# Architecture

## Initial architecture

The system starts as a modular monolith:

```text
React + TypeScript + Vite
            |
            v
FastAPI modular monolith
      |             |
      v             v
PostgreSQL     Local file storage
```

The frontend and backend have clear API and module boundaries, but they are developed and deployed as a small number of local services. CSV processing is initially an application service invoked by the backend. This keeps the first version easy to run, debug, and test.

## EC2 learning deployment

For the EC2 learning deployment, a production Nginx image serves the built React assets and is the only public application entry point. It forwards `/api/` requests to FastAPI over a private Docker network. The browser uses same-origin `/api/` URLs, avoiding a separate public API origin and its CORS configuration. The Nginx image is built from `docker/Dockerfile`, which first builds the frontend with Node.js and then copies the static output into Nginx.

```text
Browser -> EC2 Elastic IP:80 -> Nginx gateway
                                  |-> static React assets
                                  `-> backend:8000 (/api/)
```

## Responsibilities

### Frontend

- Present registration, login, upload, status, results, and download workflows.
- Track authenticated UI state without treating the browser as the authorization boundary.
- Validate obvious input constraints for fast feedback.
- Call versioned backend APIs and render server errors consistently.
- Avoid embedding processing or authorization rules in client code.

### Backend

- Expose the HTTP API and enforce authentication and authorization.
- Validate request data and upload constraints.
- Coordinate users, file metadata, processing jobs, and results.
- Parse and process CSV data through an isolated service module.
- Return stable status and result representations.
- Emit structured logs and expose health/readiness endpoints.

Suggested backend modules are `auth`, `users`, `files`, `processing`, and `common`. These are logical modules in one deployable application, not separate services.

### PostgreSQL

PostgreSQL stores durable application state: users, file metadata, processing status, processing timestamps, summary results, and references to stored files. It should not store raw file bytes initially. Database transactions protect metadata state transitions and user ownership relationships.

### Local file storage

Store uploads and generated outputs under a configured application data directory outside the source tree. Persist only opaque storage keys or paths in PostgreSQL. Never construct a path directly from an untrusted filename. A storage interface should keep the eventual move to S3 localized, but no cloud adapter is needed now.

### Authentication

Use application-managed accounts for the learning MVP: email or username, password hash, and a server-issued authenticated session. The exact token/session mechanism must be chosen before implementation. A secure, HTTP-only cookie-backed session is a reasonable default for a same-origin deployment; a short-lived access token plus refresh strategy is an alternative with more client complexity. Authorization must be enforced server-side for every file operation.

### CSV processing

Begin with synchronous processing in a backend service for bounded files. Stream rows where possible, avoid loading unnecessarily large files into memory, and return a durable processing record even when processing fails. Keep parsing, validation, duplicate detection, and statistics computation independent from HTTP handlers so the same logic can later run in a worker.

A processing state machine should use explicit states such as `queued`, `processing`, `completed`, and `failed`, even if the first implementation transitions immediately. This makes the later asynchronous migration less disruptive.

## Data ownership model

Each file belongs to exactly one user. Processing records and results belong to that file and inherit its access scope. API queries must filter by authenticated user ownership rather than trusting an ID supplied by the client.

## Repository structure

```text
/
├── AGENTS.md
├── backend/              # FastAPI application and backend tests (future milestone)
├── frontend/             # React/Vite application and frontend tests (future milestone)
├── docs/                 # Requirements, architecture, development, roadmap
├── docker/               # Dockerfiles and supporting local container configuration (future)
├── storage/              # Local runtime data; ignored by version control (future)
├── docker-compose.yml    # Local orchestration (future milestone)
└── .gitignore            # Secrets, generated files, and runtime storage (future)
```

This is intentionally a conventional monorepo. It keeps frontend and backend concerns visible, supports a single local development workflow, and leaves room for Docker without pretending that container or deployment configuration already exists.

## Architectural guardrails

- Do not split the monolith into services until there is a measured operational or scaling problem.
- Do not add a queue, cache, or worker solely because it is a common AWS pattern.
- Keep domain logic independent of FastAPI, PostgreSQL, and local storage where practical.
- Introduce interfaces at real replacement boundaries, especially file storage and processing execution; avoid speculative frameworks.
- Record meaningful changes in this document and the roadmap before implementation.

## Future AWS evolution

AWS adoption should follow a concrete problem and preserve the local development path.

| Service or change | Problem it solves | Benefit | Complexity introduced | Justification threshold |
| --- | --- | --- | --- | --- |
| Local storage to S3 | Files need durable, scalable storage beyond one application host | High durability, independent object storage, lifecycle policies, and easier horizontal scaling | Bucket policy/IAM design, network access, transfer costs, cleanup, and local emulation or test seams | Adopt when files must survive host replacement, multiple app instances need access, or retention grows beyond local storage |
| PostgreSQL to RDS | The team should not operate database backups, patching, and failover | Managed backups, monitoring, and a production-ready database endpoint | AWS networking, migrations against remote infrastructure, cost, and connection management | Adopt for a real hosted environment or when database operations become the dominant reliability risk |
| Synchronous processing to SQS plus worker | Large files or concurrent uploads make requests slow, unreliable, or resource-heavy | Retries, buffering, independent worker scaling, and responsive status updates | At-least-once delivery, idempotency, visibility timeouts, dead-letter queues, deployment of another runtime, and harder local debugging | Adopt when measured processing duration, concurrency, or failure recovery makes request-bound work inadequate |
| Worker runtime to ECS, Lambda, or another managed runtime | Worker deployment and scaling become operational work | Managed execution and resource scaling | Service-specific limits, IAM, packaging, cold starts or task management, and more deployment concepts | Choose only after the worker contract and workload profile are known; do not choose the runtime first |
| Application logs to CloudWatch | Logs from multiple hosted components need central search, retention, and alarms | Centralized operational visibility and AWS integration | Log costs, retention configuration, structured logging requirements, and AWS permissions | Adopt with the first hosted environment or when local logs cannot diagnose production incidents |
| Metrics/traces to AWS observability tools | Latency, failures, queue depth, and processing health need measurable alerts | Detection of regressions and capacity problems | Instrumentation, dashboards, sampling, cardinality and storage costs | Adopt when the system is deployed or has background processing that cannot be monitored from request logs alone |
| Environment secrets to Secrets Manager or Parameter Store | Runtime secrets should not be copied into hosts or deployment configuration | Centralized access control, rotation support, and auditability | IAM policies, bootstrap configuration, secret retrieval failures, and service cost depending on choice | Adopt before production deployment or any environment shared by more than one operator |
| Application authentication to a managed identity provider | Account recovery, verification, and abuse controls become costly to maintain | Managed identity lifecycle, optional social login, and mature security controls | Vendor coupling, hosted-login UX, token integration, migration concerns, and less direct learning of auth internals | Adopt when account operations or security requirements exceed the learning value of app-managed auth |

These are options, not commitments. Each migration should include an explicit decision record, cost estimate, security review, local test strategy, and rollback plan.
