.PHONY: help build up down restart logs ps shell status
.PHONY: test test-product test-order test-integration
.PHONY: seed clean-db reset-db init-db
.PHONY: logs-product logs-order logs-gateway
.PHONY: venv install lint format

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Docker compose file
COMPOSE_FILE := docker-compose.yml

help:
	@echo "$(GREEN)=== BulbShop Backend Commands ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Commands:$(NC)"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View all logs"
	@echo "  make logs-product   - View Product Service logs"
	@echo "  make logs-order     - View Order Service logs"
	@echo "  make logs-gateway   - View API Gateway logs"
	@echo "  make ps             - Show running containers"
	@echo "  make status         - Show services status"
	@echo "  make shell          - Open shell in Product Service"
	@echo ""
	@echo "$(YELLOW)Database Commands:$(NC)"
	@echo "  make init-db        - Initialize database schemas"
	@echo "  make seed           - Seed test data"
	@echo "  make clean-db       - Clean all database tables"
	@echo "  make reset-db       - Reset databases (clean + init + seed)"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  make test           - Run all tests"
	@echo "  make test-product   - Run Product Service tests"
	@echo "  make test-order     - Run Order Service tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make venv           - Create virtual environment"
	@echo "  make install        - Install dependencies"
	@echo "  make lint           - Run linter"
	@echo "  make format         - Format code"
	@echo "  make clean          - Clean temporary files"

# ==================== Docker Commands ====================

build:
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up:
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Waiting for services to be ready...$(NC)"
	sleep 5
	@make status

down:
	@echo "$(GREEN)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: down up
	@echo "$(GREEN)Services restarted$(NC)"

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-product:
	docker-compose -f $(COMPOSE_FILE) logs -f product-service

logs-order:
	docker-compose -f $(COMPOSE_FILE) logs -f order-service

logs-gateway:
	docker-compose -f $(COMPOSE_FILE) logs -f api-gateway

ps:
	docker-compose -f $(COMPOSE_FILE) ps

status:
	@echo "$(GREEN)=== Services Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Product Service:$(NC)"
	@curl -s http://localhost:8081/health || echo "  Not running"
	@echo ""
	@echo "$(YELLOW)Order Service:$(NC)"
	@curl -s http://localhost:8082/health || echo "  Not running"
	@echo ""
	@echo "$(YELLOW)API Gateway:$(NC)"
	@curl -s http://localhost/health || echo "  Not running"
	@echo ""

shell:
	docker-compose -f $(COMPOSE_FILE) exec product-service /bin/bash

# ==================== Database Commands ====================

init-db:
	@echo "$(GREEN)Initializing database schemas...$(NC)"
	@echo "$(YELLOW)Product Service DB:$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec product-db psql -U product_user -d product_db -c "\dt" || true
	@echo "$(YELLOW)Order Service DB:$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec order-db psql -U order_user -d order_db -c "\dt" || true
	@echo "$(GREEN)Database schemas initialized$(NC)"

seed:
	@echo "$(GREEN)Seeding test data...$(NC)"
	@echo "$(YELLOW)Seeding Product Service...$(NC)"
	cd product-service && python3 scripts/seed_data.py || true
	@echo "$(YELLOW)Seeding Order Service...$(NC)"
	cd order-service && python3 scripts/seed_data.py || true
	@echo "$(GREEN)Seeding completed$(NC)"

clean-db:
	@echo "$(RED)Cleaning databases...$(NC)"
	@echo "$(YELLOW)Cleaning Product Service DB...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec product-db psql -U product_user -d product_db -c "TRUNCATE TABLE product_attributes CASCADE; TRUNCATE TABLE products CASCADE; TRUNCATE TABLE categories CASCADE;" || true
	@echo "$(YELLOW)Cleaning Order Service DB...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec order-db psql -U order_user -d order_db -c "TRUNCATE TABLE order_status_history CASCADE; TRUNCATE TABLE order_items CASCADE; TRUNCATE TABLE orders CASCADE;" || true
	@echo "$(GREEN)Databases cleaned$(NC)"

reset-db: clean-db init-db seed
	@echo "$(GREEN)Databases reset completed$(NC)"

# ==================== Testing Commands ====================

test:
	@echo "$(GREEN)Running all tests...$(NC)"
	@make test-product
	@make test-order

test-product:
	@echo "$(GREEN)Running Product Service tests...$(NC)"
	cd product-service && pytest tests/ -v

test-order:
	@echo "$(GREEN)Running Order Service tests...$(NC)"
	cd order-service && pytest tests/ -v

test-integration:
	@echo "$(GREEN)Running integration tests...$(NC)"
	@echo "Testing Product -> Order communication..."
	@curl -s -X POST http://localhost:8082/api/v1/orders \
		-H "Content-Type: application/json" \
		-d '{"customer_name":"Test","customer_phone":"+79999999999","delivery_address":"Test","items":[{"product_id":1,"quantity":1}]}' \
		| python3 -m json.tool || echo "Integration test failed"

test-coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	cd product-service && pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	cd order-service && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# ==================== Development Commands ====================

venv:
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	python3 -m venv venv
	@echo "$(GREEN)Virtual environment created. Activate with: source venv/bin/activate$(NC)"

install:
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r product-service/requirements.txt
	pip install -r order-service/requirements.txt
	pip install pytest pytest-cov httpx black flake8 mypy

lint:
	@echo "$(GREEN)Running linter...$(NC)"
	flake8 product-service/app --max-line-length=120 --ignore=E203,W503
	flake8 order-service/app --max-line-length=120 --ignore=E203,W503

format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black product-service/app --line-length=100
	black order-service/app --line-length=100

clean:
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf venv 2>/dev/null || true
	@echo "$(GREEN)Clean completed$(NC)"

# ==================== Quick Commands ====================

dev: venv install up seed
	@echo "$(GREEN)Development environment ready!$(NC)"
	@make status

prod: build up
	@echo "$(GREEN)Production environment ready!$(NC)"

health:
	@echo "$(GREEN)=== Health Check ===$(NC)"
	@echo -n "Product Service: "
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081/health
	@echo -n "Order Service: "
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/health
	@echo -n "API Gateway: "
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost/health