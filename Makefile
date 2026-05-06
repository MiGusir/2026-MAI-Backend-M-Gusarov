COMPOSE = docker compose

.PHONY: build up down logs migrate seed migrate-status reset

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) up -d db
	@echo "Waiting for PostgreSQL..."
	@until $(COMPOSE) exec -T db pg_isready -U app -d netbox >/dev/null 2>&1; do sleep 1; done
	$(COMPOSE) run --rm app alembic upgrade head
	@echo "Migration completed successfully."

seed:
	$(COMPOSE) up -d db
	@echo "Waiting for PostgreSQL..."
	@until $(COMPOSE) exec -T db pg_isready -U app -d netbox >/dev/null 2>&1; do sleep 1; done
	$(COMPOSE) run --rm app python seed.py
	@echo "Seed command completed."

migrate-status:
	$(COMPOSE) run --rm app alembic current

reset:
	$(COMPOSE) down -v
