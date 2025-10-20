# =============================================================================
# WALACOR FINANCIAL INTEGRITY - BACKEND MAKEFILE
# =============================================================================
# This Makefile provides convenient commands for database migrations,
# development, and deployment tasks.
#
# Usage:
#   make help          - Show available commands
#   make migrate       - Generate new migration from model changes
#   make upgrade       - Apply pending migrations
#   make downgrade     - Rollback last migration
#   make current       - Show current migration version
#   make history       - Show migration history
#   make reset-db      - Reset database (WARNING: destroys all data)
# =============================================================================

# Default database URL (can be overridden with environment variable)
DATABASE_URL ?= sqlite:///./integrityx.db

# Python executable
PYTHON := python

# Alembic executable
ALEMBIC := alembic

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help migrate upgrade downgrade current history reset-db install test clean

# Default target
help: ## Show this help message
	@echo "$(BLUE)Walacor Financial Integrity - Backend Commands$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Database Migration Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(migrate|upgrade|downgrade|current|history|reset-db)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(install|test|clean|run|dev)"
	@echo ""
	@echo "$(GREEN)Environment:$(NC)"
	@echo "  DATABASE_URL = $(DATABASE_URL)"
	@echo ""

# =============================================================================
# DATABASE MIGRATION COMMANDS
# =============================================================================

migrate: ## Generate new migration from model changes
	@echo "$(BLUE)Generating new migration...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✅ Migration generated successfully!$(NC)"
	@echo "$(YELLOW)💡 Run 'make upgrade' to apply the migration$(NC)"

migrate-manual: ## Generate empty migration file for manual changes
	@echo "$(BLUE)Generating empty migration...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) revision -m "$(MSG)"
	@echo "$(GREEN)✅ Empty migration generated successfully!$(NC)"

upgrade: ## Apply pending migrations to database
	@echo "$(BLUE)Applying migrations...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) upgrade head
	@echo "$(GREEN)✅ Migrations applied successfully!$(NC)"

downgrade: ## Rollback last migration
	@echo "$(YELLOW)⚠️  Rolling back last migration...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) downgrade -1
	@echo "$(GREEN)✅ Migration rolled back successfully!$(NC)"

current: ## Show current migration version
	@echo "$(BLUE)Current migration version:$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) current

history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) history

reset-db: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all data in the database!$(NC)"
	@echo "$(YELLOW)Are you sure? Type 'yes' to continue:$(NC)"
	@read confirm && [ "$$confirm" = "yes" ] || (echo "$(RED)❌ Operation cancelled$(NC)" && exit 1)
	@echo "$(BLUE)Resetting database...$(NC)"
	@rm -f integrityx.db
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) upgrade head
	@echo "$(GREEN)✅ Database reset successfully!$(NC)"

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

install: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@pip install -r ../requirements.txt
	@pip install alembic
	@echo "$(GREEN)✅ Dependencies installed successfully!$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)✅ Tests completed!$(NC)"

run: ## Run the FastAPI development server
	@echo "$(BLUE)Starting FastAPI development server...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(PYTHON) main_simple.py

dev: ## Run development server with auto-reload
	@echo "$(BLUE)Starting development server with auto-reload...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && uvicorn main_simple:app --reload --host 0.0.0.0 --port 8000

clean: ## Clean up temporary files
	@echo "$(BLUE)Cleaning up...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

# =============================================================================
# PRODUCTION COMMANDS
# =============================================================================

prod-run: ## Run production server
	@echo "$(BLUE)Starting production server...$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && uvicorn main_simple:app --host 0.0.0.0 --port 8000 --workers 4

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

check-db: ## Check database connection and show info
	@echo "$(BLUE)Database Information:$(NC)"
	@echo "  URL: $(DATABASE_URL)"
	@echo "  Type: $$(echo $(DATABASE_URL) | cut -d: -f1)"
	@echo ""
	@echo "$(BLUE)Current Migration Status:$(NC)"
	@export DATABASE_URL=$(DATABASE_URL) && $(ALEMBIC) current

show-tables: ## Show database tables (SQLite only)
	@echo "$(BLUE)Database Tables:$(NC)"
	@sqlite3 integrityx.db ".tables"

# =============================================================================
# EXAMPLES
# =============================================================================

# Example usage:
#   make migrate MSG="Add user table"
#   make upgrade
#   make current
#   make history
#   make downgrade
#   make reset-db
#   make run
#   make dev


