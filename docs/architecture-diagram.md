# EAV Insight API — Architecture Diagram

## System Overview

```mermaid
flowchart TD
    Reviewer[Reviewer / Client / Recruiter] --> Render[Render Web Service]
    Render --> FastAPI[FastAPI Application]
    FastAPI --> Auth[JWT Authentication]
    FastAPI --> Routes[Versioned API Routes /api/v1]
    Routes --> Reports[Report API]
    Routes --> Documents[Document API]
    Routes --> Health[Health API]
    Reports --> OrgScope[Organization Scoped Access]
    Documents --> OrgScope
    OrgScope --> SQLAlchemy[SQLAlchemy Models]
    SQLAlchemy --> Postgres[(PostgreSQL)]
    FastAPI --> Errors[Consistent Error Handler]
    FastAPI --> OpenAPI[Swagger / OpenAPI Docs]
    CI[GitHub Actions CI] --> Tests[Pytest + Ruff + Alembic Check]
    Docker[Dockerfile + Docker Compose] --> FastAPI
```

## Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI API
    participant Auth as Auth Dependency
    participant DB as PostgreSQL

    Client->>API: Request with Bearer Token
    API->>Auth: Decode and validate JWT
    Auth->>DB: Load current user
    DB-->>Auth: User + organization_id
    Auth-->>API: Current user context
    API->>DB: Query organization-scoped records
    DB-->>API: Reports / Documents
    API-->>Client: JSON response or standard error envelope
```

## Core Design Choices

| Choice | Reason |
|---|---|
| FastAPI | Clean API development, validation, OpenAPI documentation |
| SQLAlchemy | Explicit relational data modelling |
| Alembic | Database migration discipline |
| PostgreSQL | Production-style relational persistence |
| JWT bearer auth | Standard API authentication flow |
| Organization scoping | Multi-tenant business API behavior |
| Docker | Repeatable local and hosted runtime |
| GitHub Actions | Automated verification before merge |
| Render | Public portfolio deployment |

## Portfolio Value

This architecture demonstrates practical backend engineering: authenticated APIs, organization-scoped access, relational modelling, migrations, tests, CI, Docker, and deployment readiness.
