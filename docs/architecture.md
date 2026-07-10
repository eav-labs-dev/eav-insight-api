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
- organization-scoped report CRUD routes
- organization-scoped document CRUD routes
- request/response schemas
- database session dependency
- SQLAlchemy models and relationships
- search/filtering queries
- deterministic sorting controls
- enriched limit/offset pagination responses

## Planned MVP Components

- service layer extraction if route complexity grows
- tag management endpoints
- organization and user endpoints
- role-aware authorization helpers
- background processing placeholder using Redis
- file upload/storage integration

## Authentication Design

The current authentication layer is intentionally small but functional:

- users register under an existing organization
- passwords are stored as salted PBKDF2-SHA256 hashes
- login returns a signed JWT bearer token
- `/auth/me` validates the token and returns the current user

Report and document access is now protected by bearer authentication and scoped by the current user's organization. Cross-organization access returns `404` so callers cannot enumerate records outside their workspace.

## Search and Pagination Design

List routes keep query logic close to the API layer for now because the MVP is
still small. The current implementation supports common operational workflows:

- text search over report and document metadata
- exact filters for workflow status, source, content type, and linked records
- date and size range filters where they matter
- deterministic sorting for stable API results
- pagination metadata that supports frontend and mobile list views

A service/repository layer can be extracted later if filtering rules become more
complex.

## Engineering Notes

This repository should stay intentionally simple while the MVP is built. Prefer readable structure, documented commands, and real working endpoints over premature abstraction.


## Authorization Design

The first authorization layer is organization scoping:

- report and document endpoints require a valid bearer token
- create operations assign `organization_id` from the current user
- list operations filter by the current user's organization
- detail, update, and delete operations only resolve records in the current user's organization
- cross-organization report/document links are rejected

Role-aware authorization can be added after the MVP routes stabilize.
