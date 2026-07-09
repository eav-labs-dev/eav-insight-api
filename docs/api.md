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
- reports
- documents
- tags
- search
- pagination
