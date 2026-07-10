# EAV Insight API — API Notes

## Base URL

Local development:

```text
http://localhost:8000
```

## Versioned Prefix

```text
/api/v1
```

## Authentication Model

Public endpoints:

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/token`

Protected business endpoints require:

```text
Authorization: Bearer <access_token>
```

Reports and documents are scoped to the authenticated user's organization. Clients do not send `organization_id` when creating report or document records. The API derives the organization from the current user and returns `404` when a record is outside that organization.

## Current Endpoints

### GET `/`

Returns basic service metadata.

### GET `/api/v1/health`

Returns health check status.

Example response:

```json
{
  "status": "ok",
  "service": "EAV Insight API",
  "environment": "development"
}
```

## Authentication

### POST `/api/v1/auth/register`

Creates a user account under an existing organization. The organization must already exist.

Example request:

```json
{
  "organization_id": "organization-uuid",
  "email": "admin@example.com",
  "full_name": "Demo Admin",
  "password": "ChangeMe123!",
  "role": "admin"
}
```

Example response:

```json
{
  "id": "user-uuid",
  "organization_id": "organization-uuid",
  "email": "admin@example.com",
  "full_name": "Demo Admin",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-07-10T00:00:00Z",
  "updated_at": "2026-07-10T00:00:00Z"
}
```

### POST `/api/v1/auth/token`

Authenticates a user and returns a bearer token.

Example request:

```json
{
  "email": "admin@example.com",
  "password": "ChangeMe123!"
}
```

Example response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### GET `/api/v1/auth/me`

Returns the current authenticated user.

Required header:

```text
Authorization: Bearer <access_token>
```

## Reports

All report routes require a bearer token.

### POST `/api/v1/reports`

Creates a report record under the authenticated user's organization.

Example request:

```json
{
  "title": "Daily Field Operations",
  "summary": "Field report for inspection activity.",
  "status": "submitted",
  "source": "mobile-app",
  "tag_ids": ["tag-uuid"]
}
```

### GET `/api/v1/reports`

Lists reports in the authenticated user's organization with pagination and optional filters.

Supported query parameters:

| Parameter | Purpose |
|---|---|
| `search` | Search title, summary, and source |
| `status` | Filter by report status |
| `source` | Filter by exact source value, such as `mobile-app` |
| `tag_id` | Filter by linked tag ID |
| `reported_from` | Filter reports on or after this reported timestamp |
| `reported_to` | Filter reports on or before this reported timestamp |
| `sort_by` | Sort by `created_at`, `reported_at`, `title`, or `status` |
| `sort_order` | Sort using `asc` or `desc` |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

Example:

```text
/api/v1/reports?search=field&status=submitted&source=mobile-app&limit=20&offset=0
```

### GET `/api/v1/reports/{report_id}`

Returns one organization-visible report by ID.

### PATCH `/api/v1/reports/{report_id}`

Updates report fields such as title, summary, status, source, reported date, or tag links.

### DELETE `/api/v1/reports/{report_id}`

Deletes a report record visible to the authenticated user.

## Documents

All document routes require a bearer token.

### POST `/api/v1/documents`

Registers a document record under the authenticated user's organization. File upload/storage is intentionally not implemented yet; this endpoint stores document metadata and storage reference paths.

Example request:

```json
{
  "report_id": "report-uuid",
  "filename": "safety-inspection.pdf",
  "content_type": "application/pdf",
  "storage_path": "demo/safety-inspection.pdf",
  "size_bytes": 4096
}
```

### GET `/api/v1/documents`

Lists documents in the authenticated user's organization with pagination and optional filters.

Supported query parameters:

| Parameter | Purpose |
|---|---|
| `search` | Search filename, storage path, and content type |
| `report_id` | Filter by linked report |
| `content_type` | Filter by exact MIME/content type |
| `min_size_bytes` | Filter documents with at least this size |
| `max_size_bytes` | Filter documents with at most this size |
| `sort_by` | Sort by `created_at`, `filename`, `content_type`, or `size_bytes` |
| `sort_order` | Sort using `asc` or `desc` |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

### GET `/api/v1/documents/{document_id}`

Returns one organization-visible document by ID.

### PATCH `/api/v1/documents/{document_id}`

Updates document metadata.

### DELETE `/api/v1/documents/{document_id}`

Deletes a document record visible to the authenticated user.

## Pagination Response Shape

List endpoints return a consistent pagination object:

```json
{
  "items": [],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0,
    "count": 10,
    "has_next": true,
    "has_previous": false,
    "next_offset": 10,
    "previous_offset": null
  }
}
```

This gives frontend or mobile clients enough metadata to build paginated list
views without guessing whether another page exists.


## Error Response Shape

All handled HTTP and validation errors use a consistent error envelope.

Example not-found response:

```json
{
  "error": {
    "code": "not_found",
    "message": "Report not found.",
    "details": []
  }
}
```

Example validation response:

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

Current standard codes include:

| Code | Typical status | Meaning |
|---|---:|---|
| `bad_request` | 400 | The request is syntactically valid but cannot be accepted |
| `unauthorized` | 401 | The caller is missing or has supplied invalid credentials |
| `forbidden` | 403 | The caller is authenticated but not allowed to perform the action |
| `not_found` | 404 | The resource does not exist or is not visible to the caller |
| `conflict` | 409 | The request conflicts with an existing resource |
| `validation_error` | 422 | Request data failed schema validation |

This makes frontend, mobile, and integration clients easier to build because
they can consistently read `error.code`, `error.message`, and `error.details`.

## Demo Request Walkthrough

A full reviewer-friendly curl walkthrough is available in [`api-examples.md`](api-examples.md).

After running migrations and seeding demo data, use:

```bash
make demo-api
```

This logs in with the seeded demo user, creates a report, registers document
metadata, exercises search/filter/pagination, and shows the standardized error
response shape.

## OpenAPI Docs

FastAPI generates Swagger documentation automatically:

```text
http://localhost:8000/docs
```

ReDoc documentation:

```text
http://localhost:8000/redoc
```

## Data Model Areas

The current database foundation includes:

- organizations
- users
- reports
- documents
- tags

See [`database.md`](database.md) for table and migration notes.

## Planned API Areas

- organizations
- users
- tags
- role-aware authorization helpers
- file upload/storage integration
- background processing placeholder
