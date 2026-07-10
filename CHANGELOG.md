# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Render deployment Blueprint with Docker web service and managed PostgreSQL configuration.
- Render release script for Alembic migration execution before service startup.
- Deployment smoke-check script and `make check-deploy` command.
- Render-specific deployment guide in `docs/deployment-render.md`.
- Hosted PostgreSQL URL normalization for provider-supplied database connection strings.
- Configuration tests for SQLAlchemy database URL normalization.
- Reviewer-friendly API demo request walkthrough in `docs/api-examples.md`.
- `scripts/demo_api_flow.sh` for a curl-based login, report, document, filtering, and error-response demo.
- `make demo-api` command for quickly exercising the seeded API workflow.
- Development workflow documentation for host-based, Docker-only, and demo API flows.
- Seed script output showing local demo login credentials.
- Docker and CI polish with container health checks, migration verification, and Docker image build checks.
- Development workflow documentation covering host-based and Docker-only setup.
- Makefile commands for standard verification, Docker build, Docker logs, container migrations, and container seeding.
- Deployment documentation updates for container runtime, migration, health-check, and CI expectations.
- Centralized HTTP and validation error handlers.
- Standard `{ "error": { "code", "message", "details" } }` response envelope.
- Error response schemas and tests for auth, not-found, and validation failures.
- README, API, architecture, deployment, and roadmap documentation updates for error handling.
- Advanced report filters for source, tag, reported date range, sorting, and pagination metadata.
- Advanced document filters for report, content type, file size range, sorting, and pagination metadata.
- API tests covering report/document search, filtering, sorting, and paginated responses.
- README, API, architecture, and roadmap documentation updates for search/filter pagination behavior.
- Organization-scoped authorization for report and document endpoints.
- Bearer-token protection for report and document create/list/detail/update/delete routes.
- Access-control tests for unauthenticated and cross-organization report/document access.
- README, API, architecture, database, deployment, and roadmap documentation updates for secured business endpoints.
- Authentication foundation with user registration, JWT token issuance, and current-user endpoint.
- Password hashing helpers using salted PBKDF2-SHA256.
- Auth schemas, route dependencies, and bearer-token validation.
- Alembic migration for user password hash storage.
- Auth API tests covering registration, login, duplicate users, invalid passwords, and token validation.
- README and API documentation updates for authentication workflow.
- Report CRUD endpoints with search, filtering, pagination, and tag linking.
- Document CRUD endpoints with search, filtering, pagination, and report validation.
- Pydantic request/response schemas for reports, documents, and pagination.
- API tests covering report and document create/list/update/delete workflows.
- Updated API documentation with report and document endpoint examples.
- SQLAlchemy core models for organizations, users, reports, documents, and tags.
- Alembic migration setup with initial core tables migration.
- Demo seed data script for local development.
- Database model tests.
- Database documentation and Makefile commands.
- FastAPI application foundation.
- Health check endpoint.
- Environment-based settings.
- Dockerfile and Docker Compose setup.
- Pytest foundation.
- Ruff linting configuration.
- GitHub Actions CI workflow.
- Initial documentation folder.
