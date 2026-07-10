# EAV Insight API — Deployment Notes

## Status

Deployment is not yet finalized. This document tracks the deployment requirements for the MVP.

## Runtime Requirements

- Python 3.12+
- PostgreSQL
- Redis
- environment variables configured from `.env.example`

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

## Deployment Direction

The first public deployment should prioritize reliability and simple reviewability over complex infrastructure. A small container-friendly platform or VM is sufficient for the MVP.


## Authentication Secrets

Production-like deployments must provide these authentication values through the hosting provider secret/environment configuration:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
PASSWORD_HASH_ITERATIONS
```

Use a long random `JWT_SECRET_KEY`. Do not reuse the local development value from `.env.example`.


## Authorization Behavior

Protected report and document routes require JWT bearer authentication. Production deployments must keep `JWT_SECRET_KEY` private and rotate it if it is exposed.

Organization scoping is enforced at the API layer using the current user from the bearer token. Deployment smoke tests should include an authenticated request to `/api/v1/reports`.
