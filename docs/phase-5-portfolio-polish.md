# EAV Insight API — Phase 5 Portfolio Polish

## Objective

Complete the final presentation layer for `eav-insight-api` so the repository is easy to evaluate by recruiters, senior engineers, and potential clients.

## Phase 5 Checklist

- [ ] add CI badge after repository path is finalized
- [ ] add architecture diagram
- [ ] add screenshots or Swagger screenshots
- [x] add reviewer-friendly API examples
- [x] add deployment notes
- [x] add Render deployment Blueprint and smoke-check script
- [ ] create LinkedIn launch summary

## Task 1 — Add CI Badge

Use the final GitHub repository path.

Template:

```md
[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)
```

Place it directly under the README title.

## Task 2 — Add Architecture Diagram

Add:

```text
docs/architecture-diagram.md
```

Then link it from:

```text
README.md
docs/architecture.md
```

## Task 3 — Add Screenshots

Create:

```text
docs/assets/screenshots/
```

Recommended screenshots:

- live root endpoint
- health endpoint
- Swagger/OpenAPI page
- auth endpoints
- report/document endpoints
- GitHub Actions passing CI
- Render successful deployment

## Task 4 — Add LinkedIn Launch Summary

Create:

```text
docs/linkedin-launch-summary.md
```

Use it as the announcement draft when presenting EAV Insight as the first EAV Labs project.

## Completion Definition

Phase 5 is complete when:

- README has a CI badge
- README links to the live API
- README links to architecture docs
- architecture diagram exists
- screenshots or screenshot guide exists
- LinkedIn launch summary exists
- roadmap marks Phase 5 complete
- `v0.1.0` release tag is created

## Recommended Branch

```bash
git checkout dev
git pull origin dev

git checkout -b docs/phase-5-portfolio-polish
```

## Recommended Commit

```bash
git add .
git commit -m "docs: complete Phase 5 portfolio polish"
git push -u origin docs/phase-5-portfolio-polish
```
