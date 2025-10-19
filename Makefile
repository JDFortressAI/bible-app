# Bible Chat Development Makefile

.PHONY: help install test run clean docker-build docker-run test-s3

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	uv sync

test: ## Run tests
	uv run pytest tests/ -v

test-s3: ## Test S3 cache functionality
	uv run python test_s3_cache.py

run: ## Run the application locally
	uv run python run_local.py

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

docker-build: ## Build Docker image
	docker build -t bible-chat .

docker-run: ## Run Docker container
	docker-compose up --build

docker-stop: ## Stop Docker container
	docker-compose down

format: ## Format code using black and isort
	uv run black src/ tests/ *.py
	uv run isort src/ tests/ *.py

lint: ## Lint code using flake8
	uv run flake8 src/ tests/ *.py

check: format lint test ## Run all checks (format, lint, test)

dev: install test-s3 run ## Full development setup and run