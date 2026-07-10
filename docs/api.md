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
| `status` | Filter by report status |
| `search` | Search title, summary, and source |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

Example:

```text
/api/v1/reports?search=field&limit=20&offset=0
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
| `report_id` | Filter by linked report |
| `content_type` | Filter by MIME/content type |
| `search` | Search filename and storage path |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

### GET `/api/v1/documents/{document_id}`

Returns one organization-visible document by ID.

### PATCH `/api/v1/documents/{document_id}`

Updates document metadata.

### DELETE `/api/v1/documents/{document_id}`

Deletes a document record visible to the authenticated user.

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
