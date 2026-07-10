# EAV Insight API

FastAPI backend for document intake, operational reporting, and searchable business records.

## Project Status

This repository is part of the EAV Labs portfolio rebuild and is currently under active development.

## What This Project Demonstrates

EAV Insight API is designed as a production-style backend service. It demonstrates backend API design, typed Python development, environment-based configuration, Dockerized local development, automated testing, CI, and documentation discipline.

## Core Features

Current foundation:

- FastAPI application factory
- Versioned API route prefix
- Health check endpoint
- Central settings/config system
- SQLAlchemy database models
- Alembic migration setup
- Demo seed data script
- Report CRUD endpoints
- Document CRUD endpoints
- User registration and JWT authentication foundation
- Organization-scoped report and document access
- Advanced search, filtering, sorting, and pagination metadata
- Consistent API error response format
- Dockerfile
- Docker Compose with PostgreSQL and Redis
- Pytest test suite
- Ruff linting setup
- GitHub Actions CI workflow
- Documentation folder

Planned MVP features:

- organization and user API endpoints
- tag management endpoints
- background processing placeholder
- file upload/storage integration
- deployment-ready production settings

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Redis
- Docker / Docker Compose
- Pytest
- Ruff
- GitHub Actions

## Local Development

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Create environment file

```bash
cp .env.example .env
```

### 4. Run the API locally

```bash
uvicorn app.main:app --reload
```

The API should be available at:

```text
http://localhost:8000
```

Swagger/OpenAPI docs:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

## Docker Development

Start the API, PostgreSQL, and Redis:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

Remove volumes if you want a clean database reset:

```bash
docker compose down -v
```

## Authentication Configuration

Local authentication uses JWT bearer tokens and salted password hashes. Create a real secret in `.env` before running anything outside local development:

```bash
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PASSWORD_HASH_ITERATIONS=600000
```

Current auth endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/token
GET  /api/v1/auth/me
```

Use the returned token for business endpoints:

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/reports
```

Report and document endpoints now require bearer authentication. Records are automatically scoped to the authenticated user's organization, so clients do not send `organization_id` when creating reports or documents.

## Database Commands

Start PostgreSQL only:

```bash
docker compose up -d db
```

Run database migrations:

```bash
alembic upgrade head
```

Seed demo data:

```bash
python scripts/seed_demo_data.py
```

Or use the Makefile:

```bash
make db-upgrade
make seed
```

## Test Commands

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Format code:

```bash
ruff format .
```

Or use the Makefile:

```bash
make install
make test
make lint
make dev
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Basic service metadata |
| GET | `/api/v1/health` | Health check endpoint |
| POST | `/api/v1/auth/register` | Register a user under an organization |
| POST | `/api/v1/auth/token` | Authenticate and return a bearer token |
| GET | `/api/v1/auth/me` | Return the current authenticated user |
| POST | `/api/v1/reports` | Create an authenticated organization-scoped report record |
| GET | `/api/v1/reports` | Search, filter, sort, and paginate organization-scoped reports |
| GET | `/api/v1/reports/{id}` | Get a report by ID |
| PATCH | `/api/v1/reports/{id}` | Update a report |
| DELETE | `/api/v1/reports/{id}` | Delete a report |
| POST | `/api/v1/documents` | Register an authenticated organization-scoped document record |
| GET | `/api/v1/documents` | Search, filter, sort, and paginate organization-scoped documents |
| GET | `/api/v1/documents/{id}` | Get a document by ID |
| PATCH | `/api/v1/documents/{id}` | Update a document |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

## Search, Filtering, and Pagination

Report and document list endpoints support practical business API query controls.

Reports can be searched and filtered by:

```text
search
status
source
tag_id
reported_from
reported_to
sort_by
sort_order
limit
offset
```

Documents can be searched and filtered by:

```text
search
report_id
content_type
min_size_bytes
max_size_bytes
sort_by
sort_order
limit
offset
```

List responses include pagination metadata with `total`, `count`, `has_next`,
`has_previous`, `next_offset`, and `previous_offset` so clients can build real
paginated workflows.


## Error Response Format

API errors use a consistent response envelope:

```json
{
  "error": {
    "code": "not_found",
    "message": "Report not found.",
    "details": []
  }
}
```

Validation errors include field-level details so API clients can show useful form
messages:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "field": "body.title",
        "message": "String should have at least 2 characters",
        "type": "string_too_short"
      }
    ]
  }
}
```

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── documents.py
│   │   ├── reports.py
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── error_handlers.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   ├── organization.py
│   │   ├── user.py
│   │   ├── report.py
│   │   ├── document.py
│   │   └── tag.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── document.py
│   │   ├── error.py
│   │   ├── health.py
│   │   └── report.py
│   └── main.py
├── alembic/
├── docs/
├── scripts/
├── tests/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md).

## Portfolio Value

This project is intended to show that EAV Labs can design and ship a clean backend service with practical product thinking, documented setup, automated checks, and deployment-ready structure.
