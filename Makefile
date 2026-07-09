.PHONY: install dev test lint format docker-up docker-down db-upgrade db-downgrade db-revision seed clean

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

docker-up:
	docker compose up --build

docker-down:
	docker compose down

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-revision:
	alembic revision --autogenerate -m "$(message)"

seed:
	python scripts/seed_demo_data.py

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage
