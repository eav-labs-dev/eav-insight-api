.PHONY: install dev test lint format check ci docker-build docker-up docker-down docker-logs docker-shell docker-migrate docker-seed db-upgrade db-downgrade db-revision migration-check seed demo-api check-deploy clean

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

check: lint test migration-check

ci: check

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api

docker-shell:
	docker compose exec api sh

docker-migrate:
	docker compose exec api alembic upgrade head

docker-seed:
	docker compose exec api python scripts/seed_demo_data.py

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-revision:
	alembic revision --autogenerate -m "$(message)"

migration-check:
	DATABASE_URL=sqlite+pysqlite:////tmp/eav_insight_migration_check.db alembic upgrade head

seed:
	python scripts/seed_demo_data.py

demo-api:
	./scripts/demo_api_flow.sh

check-deploy:
	./scripts/check_deployment.sh "$(url)"

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
	rm -f /tmp/eav_insight_migration_check.db
