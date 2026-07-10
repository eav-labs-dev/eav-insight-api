# EAV Insight API — Deployment Notes

## Status

The first deployment target is Render using Docker and Render Postgres.

The deployment goal is a public, recruiter-friendly API URL that demonstrates the service can run outside a local development machine with migrations, health checks, environment variables, and a managed PostgreSQL database.

Detailed Render steps are documented in [`docs/deployment-render.md`](deployment-render.md).

## Runtime Requirements

- Python 3.12+
- PostgreSQL
- environment variables configured from `.env.example` or the hosting provider dashboard
- ASGI server such as Uvicorn
- Docker-compatible deployment runtime

Redis remains part of the local architecture for future background-processing work, but the current API MVP does not require Redis for request handling.

## Recommended First Deployment

Use Render for the first public deployment.

This repository includes:

```text
render.yaml
scripts/render_release.sh
scripts/check_deployment.sh
```

The Blueprint defines a Docker web service and PostgreSQL database. It uses `/api/v1/health` as the health check and runs Alembic migrations before the service starts.

## Required Environment Variables

| Variable | Purpose |
|---|---|
| `APP_NAME` | service name |
| `ENVIRONMENT` | development, staging, or production |
| `DEBUG` | debug mode flag |
| `API_V1_PREFIX` | API prefix |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string or placeholder for future background workflows |
| `CORS_ORIGINS` | comma-separated allowed origins |
| `JWT_SECRET_KEY` | secret key used to sign JWT access tokens |
| `JWT_ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | access token lifetime |
| `PASSWORD_HASH_ITERATIONS` | PBKDF2 password hashing iteration count |

## Container Deployment Direction

The Dockerfile installs the application into a slim Python runtime image and runs the API with a non-root user. The local Dockerfile default command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
```

Render overrides the command through `render.yaml` so the app binds to the platform-provided `$PORT`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers
```

## Database Migrations

Migrations should be run before the application receives traffic:

```bash
alembic upgrade head
```

For Docker Compose development, run:

```bash
docker compose exec api alembic upgrade head
```

For Render, migrations are handled by:

```bash
bash scripts/render_release.sh
```

That script currently runs:

```bash
alembic upgrade head
```

## Health Check

Use the versioned health endpoint for smoke checks:

```text
GET /api/v1/health
```

Expected production response:

```json
{
  "status": "ok",
  "service": "EAV Insight API",
  "environment": "production"
}
```

Check a deployed API with:

```bash
make check-deploy url=https://your-service-name.onrender.com
```

## Authentication Secrets

Production-like deployments must provide authentication values through the hosting provider secret/environment configuration.

Use a long random `JWT_SECRET_KEY`. Do not reuse the local development value from `.env.example`.

## Authorization Behavior

Protected report and document routes require JWT bearer authentication. Production deployments must keep `JWT_SECRET_KEY` private and rotate it if it is exposed.

Organization scoping is enforced at the API layer using the current user from the bearer token. Deployment smoke tests should include an authenticated request to `/api/v1/reports` after demo data is seeded.

## CI Expectations

GitHub Actions verifies:

- dependency installation
- Ruff linting
- pytest
- Alembic migration upgrade
- Docker image build

Render is configured to auto-deploy after checks pass.

## Error and Observability Notes

The API returns standardized error envelopes for handled HTTP and validation errors. Deployment logs should still capture unexpected exceptions through the ASGI server/runtime so production debugging does not rely on exposing internal tracebacks to API consumers.
