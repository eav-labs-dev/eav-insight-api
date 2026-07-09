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
