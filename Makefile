.PHONY: help build start stop restart logs clean test-api status

help:
	@echo "Available commands:"
	@echo "  make build       - Build all Docker images"
	@echo "  make start       - Start all services"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make status      - Show status of all services"
	@echo "  make clean       - Stop and remove all containers, volumes, and images"
	@echo "  make test-api    - Send test curl request to API"

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

restart: stop start
	@echo "Services restarted"

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	docker-compose down -v --rmi all --remove-orphans

test-api:
	@echo "Testing payout creation API..."
	@curl -X POST http://localhost/api/v1/payouts/ \
		-H "Content-Type: application/json" \
		-d '{"amount": "7000.00", "currency": "RUB", "recipient_name": "Test User", "recipient_account": "40817810099910001234", "recipient_bank": "Test Bank", "recipient_bank_code": "044525225", "description": "Testing Celery background task"}' \
		&& echo "\n"
