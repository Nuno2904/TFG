# 🛠️ Makefile for TFG FastAPI Project
# Convenient commands for development

.PHONY: help install format lint test run clean security docs

help:  ## Show this help message
	@echo "🛠️  TFG FastAPI - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install with development dependencies
	pip install -r requirements.txt
	pip install black flake8 isort mypy pytest pytest-asyncio

run:  ## Run the application
	uvicorn main:app --reload

format:  ## Format code with black and isort
	@echo "🎨 Formatting code..."
	black app/ main.py
	isort app/ main.py
	@echo "✅ Code formatted"

lint:  ## Run linting checks
	@echo "🔍 Running linting..."
	flake8 app/ main.py
	@echo "✅ Linting complete"

type-check:  ## Run type checking with mypy
	@echo "📝 Running type checks..."
	mypy app/ main.py
	@echo "✅ Type checks complete"

security:  ## Check for security vulnerabilities
	@echo "🔐 Checking security..."
	pip-audit
	@echo "✅ Security check complete"

test:  ## Run tests
	@echo "🧪 Running tests..."
	pytest -v
	@echo "✅ Tests complete"

test-cov:  ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	pytest --cov=app --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/index.html"

clean:  ## Clean up cache and build files
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	@echo "✅ Cleanup complete"

db-init:  ## Initialize the database
	@echo "🗄️  Initializing database..."
	python -c "from app.db import init_db; init_db(); print('✅ Database initialized')"

all:  ## Run format, lint, and test
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test

# 🚀 Aliases for common tasks
fmt: format
qa: lint
setup: install-dev
dev: run
