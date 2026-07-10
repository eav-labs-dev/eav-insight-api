# EAV Insight API — Reviewer Screenshots Guide

## Purpose

This file defines the screenshots that should be added to the repository before the project is considered fully portfolio-polished.

Recommended location:

```text
docs/assets/screenshots/
```

## Required Screenshots

### 1. Live Root Endpoint

URL:

```text
https://eav-insight-api.onrender.com/
```

Expected response:

```json
{
  "service": "EAV Insight API",
  "status": "running",
  "docs": "/docs",
  "health": "/api/v1/health"
}
```

Suggested filename:

```text
docs/assets/screenshots/live-root-endpoint.png
```

### 2. Live Health Endpoint

URL:

```text
https://eav-insight-api.onrender.com/api/v1/health
```

Suggested filename:

```text
docs/assets/screenshots/live-health-endpoint.png
```

### 3. Swagger / OpenAPI Docs

URL:

```text
https://eav-insight-api.onrender.com/docs
```

Suggested filename:

```text
docs/assets/screenshots/swagger-overview.png
```

### 4. Auth Endpoints in Swagger

Capture:

- `/api/v1/auth/register`
- `/api/v1/auth/token`
- `/api/v1/auth/me`

Suggested filename:

```text
docs/assets/screenshots/swagger-auth-endpoints.png
```

### 5. Report and Document Endpoints in Swagger

Capture:

- report endpoints
- document endpoints
- search/filter/pagination parameters

Suggested filename:

```text
docs/assets/screenshots/swagger-business-endpoints.png
```

### 6. GitHub Actions Passing CI

Capture a passing CI workflow run.

Suggested filename:

```text
docs/assets/screenshots/github-actions-ci.png
```

### 7. Render Deployment Success

Capture the Render service dashboard showing a successful deploy.

Suggested filename:

```text
docs/assets/screenshots/render-deployment-success.png
```

## README Screenshot Section Template

Add this after the Live Demo section when screenshots exist:

```md
## Screenshots

### OpenAPI Documentation

![Swagger overview](docs/assets/screenshots/swagger-overview.png)

### Live Health Check

![Live health endpoint](docs/assets/screenshots/live-health-endpoint.png)

### CI Status

![GitHub Actions CI](docs/assets/screenshots/github-actions-ci.png)
```
