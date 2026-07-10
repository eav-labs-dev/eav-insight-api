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
Schemas, auth dependencies, and route logic
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

## Current API Components

- auth registration, token, and current-user routes
- bearer-token current-user dependency
- password hashing and JWT helpers
- report CRUD routes
- document CRUD routes
- request/response schemas
- database session dependency
- SQLAlchemy models and relationships
- search/filtering queries
- limit/offset pagination responses

## Planned MVP Components

- service layer extraction if route complexity grows
- tag management endpoints
- organization and user endpoints
- organization-scoped authorization checks
- background processing placeholder using Redis
- file upload/storage integration

## Authentication Design

The current authentication layer is intentionally small but functional:

- users register under an existing organization
- passwords are stored as salted PBKDF2-SHA256 hashes
- login returns a signed JWT bearer token
- `/auth/me` validates the token and returns the current user

Authorization is not fully enforced across business endpoints yet. The next step is to protect write operations and scope all report/document access by organization.

## Engineering Notes

This repository should stay intentionally simple while the MVP is built. Prefer readable structure, documented commands, and real working endpoints over premature abstraction.
