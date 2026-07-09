# Contributing

This repository is part of the EAV Labs portfolio rebuild.

## Branch Naming

Use clear branch names:

```text
feature/<short-description>
fix/<short-description>
docs/<short-description>
chore/<short-description>
```

## Commit Style

Use Conventional Commits:

```text
feat: add report search endpoint
fix: correct health response
chore: configure CI workflow
docs: update setup guide
test: add health endpoint tests
```

## Local Checks

Before opening a pull request, run:

```bash
ruff check .
pytest
```

## Pull Request Standard

Each PR should include:

- clear summary
- what changed
- how it was tested
- screenshots or API examples where useful
