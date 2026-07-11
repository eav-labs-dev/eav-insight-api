# EAV Insight API — Development Workflow

This document explains the main local development paths for EAV Insight API.

## Recommended Host-Based Workflow

Use this when you want fast Python feedback from your Mac while PostgreSQL and Redis run in Docker.

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
docker compose up -d db redis
alembic upgrade head
python scripts/seed_demo_data.py
uvicorn app.main:app --reload
```

Run verification before committing:

```bash
make check
```

This runs Ruff, pytest, and an Alembic migration check.

## Docker-Only Workflow

Use this when you want to validate the containerized setup.

```bash
cp .env.example .env
docker compose up --build
```

In another terminal:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_demo_data.py
```

The API is available at:

```text
http://localhost:8000
```

Swagger/OpenAPI is available at:

```text
http://localhost:8000/docs
```

## Demo Credentials

The seed script creates a local demo user:

```text
Email: admin@example.com
Password: ChangeMe123!
```

These credentials are for local development only. They must not be used in deployed environments.

## Demo API Flow

After the API is running and demo data has been seeded, run:

```bash
make demo-api
```

This executes `scripts/demo_api_flow.sh`, which demonstrates the API through real HTTP requests:

- health check
- login
- current-user lookup
- report creation
- report search/filter/pagination
- document metadata creation
- document search/filter/pagination
- standardized validation error response

The script uses `curl` and Python standard-library JSON parsing. It does not require `jq`.

## Common Commands

```bash
make install          # install local development dependencies
make dev              # run uvicorn with reload
make lint             # run Ruff
make test             # run pytest
make migration-check  # validate Alembic migrations against temporary SQLite
make check            # lint + test + migration check
make docker-up        # build and run Docker Compose services
make docker-migrate   # run Alembic inside the API container
make docker-seed      # seed demo data inside the API container
make demo-api         # run the host-based demo API flow
```

## Notes on Database URLs

`.env.example` uses `localhost` so host commands such as `alembic upgrade head` can connect to PostgreSQL exposed by Docker Compose.

Docker Compose overrides `DATABASE_URL` inside the API container so the app connects to PostgreSQL using the service hostname `db`.

This separation keeps both host-based and container-based workflows simple.
