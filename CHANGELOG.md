# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

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
