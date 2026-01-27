.PHONY: help backend-up migration test lint format typecheck

help:
	@echo "Available commands:"
	@echo "  make backend-up        - Start the backend services"
	@echo "  make migration         - Create a new database migration (requires MESSAGE variable)"
	@echo "  make test              - Run backend tests with pytest"
	@echo "  make lint              - Run ruff linter on backend code"
	@echo "  make format            - Format backend code with black and ruff"
	@echo "  make typecheck         - Run mypy type checker on backend code"

backend-up:
	docker compose --profile backend up --build

migration:
ifndef MESSAGE
	$(error MESSAGE is required. Usage: make migration MESSAGE='your migration message')
endif
	@echo "Starting database..."
	docker compose --profile create_migration up -d db
	@echo "Waiting for database to be ready..."
	@sleep 3
	@echo "Generating migration: $(MESSAGE)"
	docker compose --profile create_migration run --rm backend python main.py generate-migration -m "$(MESSAGE)"
	@echo "Cleaning up..."
	docker compose --profile create_migration down
	docker compose --profile backend down
	@echo "Migration created successfully!"

test:
	@echo "Running tests..."
	cd backend && pytest

lint:
	@echo "Running ruff linter..."
	cd backend && ruff check .

format:
	@echo "Formatting code with black..."
	cd backend && black .
	@echo "Organizing imports with ruff..."
	cd backend && ruff check --select I --fix .

typecheck:
	@echo "Running mypy type checker..."
	cd backend && mypy .

