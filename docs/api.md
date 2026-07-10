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

## Reports

### POST `/api/v1/reports`

Creates a report record for an existing organization.

Example request:

```json
{
  "organization_id": "organization-uuid",
  "title": "Daily Field Operations",
  "summary": "Field report for inspection activity.",
  "status": "submitted",
  "source": "mobile-app",
  "tag_ids": ["tag-uuid"]
}
```

### GET `/api/v1/reports`

Lists reports with pagination and optional filters.

Supported query parameters:

| Parameter | Purpose |
|---|---|
| `organization_id` | Filter by organization |
| `status` | Filter by report status |
| `search` | Search title, summary, and source |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

Example:

```text
/api/v1/reports?organization_id=organization-uuid&search=field&limit=20&offset=0
```

### GET `/api/v1/reports/{report_id}`

Returns one report by ID.

### PATCH `/api/v1/reports/{report_id}`

Updates report fields such as title, summary, status, source, reported date, or tag links.

### DELETE `/api/v1/reports/{report_id}`

Deletes a report record.

## Documents

### POST `/api/v1/documents`

Registers a document record. File upload/storage is intentionally not implemented yet; this endpoint stores document metadata and storage reference paths.

Example request:

```json
{
  "organization_id": "organization-uuid",
  "report_id": "report-uuid",
  "filename": "safety-inspection.pdf",
  "content_type": "application/pdf",
  "storage_path": "demo/safety-inspection.pdf",
  "size_bytes": 4096
}
```

### GET `/api/v1/documents`

Lists documents with pagination and optional filters.

Supported query parameters:

| Parameter | Purpose |
|---|---|
| `organization_id` | Filter by organization |
| `report_id` | Filter by linked report |
| `content_type` | Filter by MIME/content type |
| `search` | Search filename and storage path |
| `limit` | Page size, from 1 to 100 |
| `offset` | Number of records to skip |

### GET `/api/v1/documents/{document_id}`

Returns one document by ID.

### PATCH `/api/v1/documents/{document_id}`

Updates document metadata.

### DELETE `/api/v1/documents/{document_id}`

Deletes a document record.

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

- authentication
- organizations
- users
- tags
- file upload/storage integration
- background processing placeholder
