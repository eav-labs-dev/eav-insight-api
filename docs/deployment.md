# EAV Insight API — Deployment Notes

## Status

Deployment is not yet finalized. This document tracks the deployment requirements for the MVP and keeps the repository ready for a simple container-based deployment.

## Runtime Requirements

- Python 3.12+
- PostgreSQL
- Redis
- environment variables configured from `.env.example`
- ASGI server such as Uvicorn

## Required Environment Variables

| Variable | Purpose |
|---|---|
| `APP_NAME` | service name |
| `ENVIRONMENT` | development, staging, or production |
| `DEBUG` | debug mode flag |
| `API_V1_PREFIX` | API prefix |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `CORS_ORIGINS` | comma-separated allowed origins |
| `JWT_SECRET_KEY` | secret key used to sign JWT access tokens |
| `JWT_ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | access token lifetime |
| `PASSWORD_HASH_ITERATIONS` | PBKDF2 password hashing iteration count |

## Container Deployment Direction

The first public deployment should prioritize reliability and simple reviewability over complex infrastructure. A small container-friendly platform or VM is sufficient for the MVP.

The Dockerfile now installs the application into a slim Python runtime image and runs the API with a non-root user. The default command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
```

For local development, Docker Compose overrides the command with `--reload`. Production deployments should use the Dockerfile default command or a platform-specific equivalent without reload enabled.

## Database Migrations

Migrations should be run before the application receives traffic:

```bash
alembic upgrade head
```

For Docker Compose development, run:

```bash
docker compose exec api alembic upgrade head
```

For hosted deployments, run the same migration command as a release phase, job, or one-off command depending on the platform.

## Health Check

Use the versioned health endpoint for smoke checks:

```text
GET /api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "EAV Insight API",
  "environment": "production"
}
```

The Docker Compose API service includes a health check that calls this endpoint from inside the container.

## Authentication Secrets

Production-like deployments must provide authentication values through the hosting provider secret/environment configuration.

Use a long random `JWT_SECRET_KEY`. Do not reuse the local development value from `.env.example`.

## Authorization Behavior

Protected report and document routes require JWT bearer authentication. Production deployments must keep `JWT_SECRET_KEY` private and rotate it if it is exposed.

Organization scoping is enforced at the API layer using the current user from the bearer token. Deployment smoke tests should include an authenticated request to `/api/v1/reports`.

## CI Expectations

GitHub Actions currently verifies:

- dependency installation
- Ruff linting
- pytest
- Alembic migration upgrade
- Docker image build

This gives reviewers a fast signal that the API can be installed, tested, migrated, and containerized.

## Error and Observability Notes

The API returns standardized error envelopes for handled HTTP and validation errors. Deployment logs should still capture unexpected exceptions through the ASGI server/runtime so production debugging does not rely on exposing internal tracebacks to API consumers.
