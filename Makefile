.PHONY: help build run test clean docker-build docker-run docker-stop docker-logs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker build -t brronson .

run: ## Run the application locally
	uvicorn app.main:app --reload --host 0.0.0.0 --port 1968

test: ## Run tests
	pytest -v

test-coverage: ## Run tests with coverage
	pytest --cov=app --cov-report=html

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov

docker-build: ## Build Docker image
	docker build -t brronson .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker Compose services
	docker-compose down

docker-logs: ## Show Docker Compose logs
	docker-compose logs -f

docker-clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

install: ## Install Python dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test-docker: ## Run tests in Docker container
	docker build -t brronson .
	docker run --rm brronson pytest

format: ## Format code with black
	black app/ tests/ --line-length=79

lint: ## Lint code with flake8
	flake8 app/ tests/

check: format lint ## Run all checks (format, lint)

lint-fix: ## Auto-fix linting issues where possible
	black app/ tests/ --line-length=79
	autopep8 --in-place --recursive --aggressive --aggressive app/ tests/

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci-check: pre-commit-run test ## Run all CI checks
