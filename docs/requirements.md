# AWS File Processing Lab Requirements

## Purpose

AWS File Processing Lab is a learning-focused web application for uploading CSV files, processing them, and presenting useful data-quality and summary results. The system should begin as a production-quality modular monolith and evolve toward AWS services only when a concrete requirement justifies the added complexity.

## Product goals

- Provide a clear upload-to-results workflow for CSV files.
- Teach Python, FastAPI, React, TypeScript, PostgreSQL, Docker, testing, cloud architecture, asynchronous processing, and observability through incremental changes.
- Keep local development reproducible and inexpensive.
- Make important architectural decisions explicit and reversible where practical.

## Functional scope

The eventual MVP is expected to support:

1. User registration.
2. User login and authenticated sessions.
3. CSV upload.
4. File metadata storage.
5. CSV processing.
6. Basic statistics and data-quality checks.
7. Processing status.
8. Results display.
9. Download of the processed file.

The features above are the target boundary, not the first implementation milestone.

## Initial processing behavior

The initial processor should eventually be deterministic and explainable. At minimum, it should report total records and distinguish valid, invalid, duplicate, and incomplete records according to a documented CSV validation policy. Numeric statistics should be added only after the input and type rules are specified.

The first supported input should be a UTF-8 CSV with a header row and a bounded file size. The initial release should not promise support for arbitrary encodings, malformed delimiter conventions, spreadsheet formulas, or very large files.

## Non-functional requirements

- Validate all client input on the server; client validation is for usability only.
- Treat uploaded files as untrusted input.
- Enforce upload size, filename, content-type, and processing-time limits.
- Do not expose files or processing results across users.
- Store passwords using a proven password-hashing library; never store plaintext passwords.
- Keep secrets out of source control and logs.
- Provide structured application errors and useful health checks.
- Add unit and API tests for each implemented behavior.
- Preserve enough metadata and logs to diagnose a failed processing job without logging file contents or credentials.

## Ambiguities and decisions still required

- What CSV columns and validation rules define a valid record?
- Are duplicate records exact row duplicates, duplicate business keys, or both?
- Are missing values counted per field, per row, or both?
- Which numeric columns and statistics are required (for example, min, max, mean, and median)?
- What is the maximum upload size and maximum processing duration?
- Which output format is downloadable: original CSV, normalized CSV, annotated CSV, or a report?
- Should users be able to delete files and results? How long should data be retained?
- Is email verification, password reset, or account lockout required?
- Should a user be allowed to process multiple files concurrently?
- Which browser versions and accessibility level are supported?
- Is local authentication sufficient for the learning MVP, or is an external identity provider desired later?

Until these questions are answered, implementation should use explicit, documented defaults rather than silently expanding scope.

## Security and privacy assumptions

- Authentication and authorization are separate concerns: every file and result query must be scoped to the authenticated user.
- Uploaded files may contain personal or confidential data. Local development data must be treated as disposable and production retention must be defined before deployment.
- CSV formula injection is a risk if generated files are opened in spreadsheet software; downloaded output must either neutralize formulas or document and enforce a safe output policy.
- CSV parsing must avoid unsafe dynamic evaluation and resource exhaustion from oversized or pathological input.
- Authentication endpoints need rate limiting before public deployment.
- HTTPS, secure cookie settings or carefully scoped bearer tokens, CSRF protection where cookie authentication is used, and dependency/security updates are required for production.

## Success criteria for the MVP

A registered user can authenticate, upload a supported CSV, observe processing status, view documented summary results, and download the resulting file. A different authenticated user cannot read or download the first user's file or results. Invalid input produces a useful error without crashing the service.
