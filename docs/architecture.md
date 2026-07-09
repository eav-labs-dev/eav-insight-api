# EAV Insight API — Architecture

## Architecture Style

EAV Insight API uses a modular FastAPI structure with clear separation between application setup, route definitions, configuration, schemas, and tests.

## Current Foundation

```text
Client
  ↓
FastAPI app
  ↓
Versioned API routes: /api/v1
  ↓
Schemas and services
  ↓
PostgreSQL / Redis planned for MVP data workflows
```

## Application Layers

| Layer | Purpose |
|---|---|
| `app/main.py` | application factory, middleware, router registration |
| `app/api/` | API route definitions |
| `app/core/` | settings, configuration, shared utilities |
| `app/schemas/` | request/response models |
| `tests/` | automated tests |

## Planned MVP Components

- SQLAlchemy models for users, organizations, reports, documents, and tags
- Alembic migrations
- authentication and authorization foundation
- search/filtering service layer
- pagination utilities
- background processing placeholder using Redis

## Engineering Notes

This repository should stay intentionally simple while the MVP is built. Prefer readable structure, documented commands, and real working endpoints over premature abstraction.
