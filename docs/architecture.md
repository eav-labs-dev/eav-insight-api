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
SQLAlchemy models
  ↓
PostgreSQL for persisted business records
  ↓
Redis planned for background processing workflows
```

## Application Layers

| Layer | Purpose |
|---|---|
| `app/main.py` | application factory, middleware, router registration |
| `app/api/` | API route definitions |
| `app/core/` | settings, configuration, shared utilities |
| `app/db/` | SQLAlchemy engine, sessions, and database dependencies |
| `app/models/` | database models and relationships |
| `app/schemas/` | request/response models |
| `tests/` | automated tests |

## Planned MVP Components

- CRUD service layer for reports, documents, and tags
- authentication and authorization foundation
- search/filtering service layer
- pagination utilities
- background processing placeholder using Redis

## Engineering Notes

This repository should stay intentionally simple while the MVP is built. Prefer readable structure, documented commands, and real working endpoints over premature abstraction.
