# EAV Insight API — Render Deployment Guide

## Purpose

This guide documents the first public deployment path for EAV Insight API using Render, Docker, and Render Postgres.

The goal is a simple, recruiter-friendly production demo URL that proves the API can be deployed, migrated, and smoke-tested outside a local machine.

## Why Render for the first deployment

Render is a good first target for this portfolio MVP because it supports GitHub-connected web services, Docker-based deploys, managed environment variables, health checks, infrastructure-as-code through `render.yaml`, and managed PostgreSQL.

This repository includes a `render.yaml` Blueprint so the web service and PostgreSQL database can be provisioned from the repo with repeatable settings.

## Important cost note

The included Blueprint uses Render's free plan for the web service and database to keep the first demo inexpensive. Free Render web services may sleep after inactivity, and free PostgreSQL databases are not suitable for long-lived production data.

For a stable portfolio link, upgrade the database before relying on it long-term.

## Files added for deployment

```text
render.yaml
scripts/render_release.sh
scripts/check_deployment.sh
docs/deployment-render.md
```

## Deployment architecture

```text
GitHub dev branch
    ↓
Render Blueprint
    ↓
Docker web service: eav-insight-api
    ↓
Render Postgres: eav-insight-db
```

At deploy time:

1. Render builds the Docker image.
2. Render injects environment variables.
3. `scripts/render_release.sh` runs `alembic upgrade head`.
4. Render starts Uvicorn using the platform-provided `$PORT`.
5. Render checks `/api/v1/health` before considering the service healthy.

## Blueprint settings

The `render.yaml` file defines:

- Docker web service: `eav-insight-api`
- Postgres database: `eav-insight-db`
- deployment branch: `dev`
- health check path: `/api/v1/health`
- auto-deploy trigger: after checks pass
- pre-deploy migration command: `bash scripts/render_release.sh`
- generated `JWT_SECRET_KEY`
- database connection string sourced from Render Postgres

## Create the Render deployment

1. Push the deployment branch to GitHub.
2. Go to the Render Dashboard.
3. Create a new Blueprint.
4. Connect the `enamavornyo/eav-insight-api` repository.
5. Select the root `render.yaml` file.
6. Review the services and database Render will create.
7. Provide a production `CORS_ORIGINS` value when prompted.
8. Apply the Blueprint.

Suggested first `CORS_ORIGINS` value:

```text
https://eav-insight-api.onrender.com,http://localhost:3000,http://localhost:5173
```

Replace the Render URL with the actual service URL after creation if Render assigns a different subdomain.

## Required production environment variables

Most values are declared in `render.yaml`. These values matter most:

| Variable | Source | Notes |
|---|---|---|
| `DATABASE_URL` | Render Postgres | Referenced from `eav-insight-db` |
| `JWT_SECRET_KEY` | Render generated value | Do not commit a real secret |
| `CORS_ORIGINS` | Render dashboard prompt | Set explicitly for the deployed API/frontends |
| `ENVIRONMENT` | Blueprint | Set to `production` |
| `DEBUG` | Blueprint | Set to `false` |

## Database URL compatibility

Render commonly provides PostgreSQL URLs in a provider-standard format such as `postgres://` or `postgresql://`.

The application normalizes hosted PostgreSQL URLs to the SQLAlchemy driver format used by this project:

```text
postgresql+psycopg://...
```

This keeps local development, CI SQLite checks, Docker Compose, and hosted Render Postgres compatible.

## Verify the deployment

After Render reports a successful deployment, run:

```bash
scripts/check_deployment.sh https://your-service-name.onrender.com
```

Or with Make:

```bash
make check-deploy url=https://your-service-name.onrender.com
```

Expected health response:

```json
{
  "status": "ok",
  "service": "EAV Insight API",
  "environment": "production"
}
```

## Run the demo flow against the deployed API

The local demo script accepts a `BASE_URL` override:

```bash
BASE_URL=https://your-service-name.onrender.com make demo-api
```

This can be used after seeding demo data in the deployed database.

## Seeding demo data on Render

Do not run the seed script automatically on every deploy. It is intentionally separate from `scripts/render_release.sh`.

For a portfolio demo, seed once from the Render Shell or a one-off command:

```bash
python scripts/seed_demo_data.py
```

Demo credentials created by the seed script:

```text
Email: admin@example.com
Password: ChangeMe123!
```

If this deployment becomes public for longer-term use, change or remove demo credentials.

## Deployment smoke checklist

- [ ] Render Blueprint applies successfully.
- [ ] Docker image builds.
- [ ] Pre-deploy migration command succeeds.
- [ ] `/api/v1/health` returns `200`.
- [ ] `/docs` opens.
- [ ] Demo data is seeded once, if needed.
- [ ] `make check-deploy url=<deployed-url>` passes.
- [ ] README deployment link is updated after the final URL is known.

## Free-tier startup behavior

Render free-tier web services do not support pre-deploy commands. For this deployment, the Dockerfile starts `scripts/start_production.sh`, which runs Alembic migrations and then starts Uvicorn.

This keeps the free-tier deployment simple while still applying migrations before the API starts.
