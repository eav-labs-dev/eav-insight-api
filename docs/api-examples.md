# EAV Insight API — Demo Request Examples

This document provides a reviewer-friendly API walkthrough for EAV Insight API.

It assumes the API is running locally at:

```text
http://localhost:8000
```

## 1. Start the local stack

Docker workflow:

```bash
cp .env.example .env
docker compose up --build
```

In another terminal, run migrations and seed demo data:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo_data.py
```

Host-based workflow:

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d db redis
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload
```

Demo credentials created by the seed script:

```text
Email: admin@example.com
Password: ChangeMe123!
```

## 2. Health check

```bash
curl http://localhost:8000/api/v1/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "EAV Insight API",
  "environment": "development"
}
```

## 3. Log in and capture a bearer token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "ChangeMe123!"
  }' \
  | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')
```

Confirm the token exists:

```bash
printf '%s\n' "$TOKEN"
```

## 4. Read the current user

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

This confirms bearer authentication is working.

## 5. Create a report

```bash
REPORT_ID=$(curl -s -X POST http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Field Operations Intake",
    "summary": "Demo report created through the public API workflow.",
    "status": "submitted",
    "source": "demo-script"
  }' \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
```

Confirm the created report ID:

```bash
printf '%s\n' "$REPORT_ID"
```

## 6. List reports with search, filtering, sorting, and pagination

```bash
curl "http://localhost:8000/api/v1/reports?search=Field&status=submitted&source=demo-script&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

List responses include pagination metadata:

```json
{
  "items": [],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0,
    "count": 1,
    "has_next": false,
    "has_previous": false,
    "next_offset": null,
    "previous_offset": null
  }
}
```

## 7. Register document metadata

```bash
DOCUMENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"report_id\": \"$REPORT_ID\",
    \"filename\": \"field-operations-intake.pdf\",
    \"content_type\": \"application/pdf\",
    \"storage_path\": \"demo/field-operations-intake.pdf\",
    \"size_bytes\": 4096
  }" \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
```

Confirm the created document ID:

```bash
printf '%s\n' "$DOCUMENT_ID"
```

## 8. List documents with filters

```bash
curl "http://localhost:8000/api/v1/documents?search=field&content_type=application/pdf&min_size_bytes=1&sort_by=created_at&sort_order=desc&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

## 9. View a standardized validation error

```bash
curl -X POST http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "No"
  }'
```

Expected shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "field": "body.title",
        "message": "String should have at least 3 characters",
        "type": "string_too_short"
      }
    ]
  }
}
```

## 10. Run the automated demo script

The repository includes a convenience script for the same workflow:

```bash
make demo-api
```

Equivalent direct command:

```bash
./scripts/demo_api_flow.sh
```

Override the base URL if needed:

```bash
API_BASE_URL=http://localhost:8001 ./scripts/demo_api_flow.sh
```

## What this demonstrates

This walkthrough shows that EAV Insight API supports:

- containerized local development
- database migrations and seed data
- JWT bearer authentication
- organization-scoped business records
- report and document workflows
- search, filtering, sorting, and pagination
- consistent error response envelopes
- reviewer-friendly API verification
