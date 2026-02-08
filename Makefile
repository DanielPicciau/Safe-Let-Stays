# =============================================================================
# Safe Let Stays - Development Makefile
# =============================================================================
# Common commands for development workflow
# Usage: make <command>
# =============================================================================

.PHONY: help install run test lint clean migrate static superuser

# Default target
help:
	@echo "Safe Let Stays - Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Full setup (install + migrate + static)"
	@echo ""
	@echo "Development:"
	@echo "  make run         - Run development server"
	@echo "  make shell       - Open Django shell"
	@echo "  make migrate     - Run database migrations"
	@echo "  make migrations  - Create new migrations"
	@echo "  make static      - Collect static files"
	@echo "  make superuser   - Create superuser"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make security    - Run security audit"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code with black"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove Python cache files"
	@echo "  make clean-all   - Remove all generated files"

# =============================================================================
# Setup Commands
# =============================================================================

install:
	pip install --upgrade pip
	pip install -r requirements.txt

setup: install migrate static
	@echo "Setup complete! Run 'make run' to start the server."

# =============================================================================
# Development Commands
# =============================================================================

run:
	python manage.py runserver

shell:
	python manage.py shell

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

static:
	python manage.py collectstatic --noinput

superuser:
	python manage.py createsuperuser

# =============================================================================
# Testing Commands
# =============================================================================

test:
	python manage.py test yourapp

test-cov:
	coverage run --source='yourapp' manage.py test yourapp
	coverage report
	coverage html

security:
	python scripts/data/security_audit.py

# =============================================================================
# Code Quality Commands
# =============================================================================

lint:
	flake8 yourapp safeletstays --max-line-length=120 --exclude=migrations

format:
	black yourapp safeletstays --line-length=120
	isort yourapp safeletstays

# =============================================================================
# Cleanup Commands
# =============================================================================

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete

clean-all: clean
	rm -rf staticfiles/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

# =============================================================================
# Production Commands
# =============================================================================

prod-static:
	python manage.py collectstatic --settings=safeletstays.settings_production --noinput

prod-migrate:
	python manage.py migrate --settings=safeletstays.settings_production

prod-check:
	python manage.py check --deploy --settings=safeletstays.settings_production
