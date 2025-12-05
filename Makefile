.PHONY: help backend-up migration

help:
	@echo "Available commands:"
	@echo "  make backend-up        - Start the backend services"
	@echo "  make migration         - Create a new database migration (requires MESSAGE variable)"

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
	@echo "Migration created successfully!"

