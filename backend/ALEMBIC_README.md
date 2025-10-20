# Alembic Database Migrations

This document explains how to use Alembic for database migrations in the Walacor Financial Integrity backend.

## Overview

Alembic is a database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes over time
- Apply migrations to different environments
- Rollback changes when needed
- Generate migrations automatically from model changes

## Setup

Alembic has been configured with the following features:
- ✅ Reads database URL from `DATABASE_URL` environment variable
- ✅ Falls back to `sqlite:///./app.db` if `DATABASE_URL` is not set
- ✅ Imports models from `src.models` for autogenerate functionality
- ✅ Configured for SQLite with proper transaction handling

## Quick Start

### 1. Check Current Status
```bash
make current
```

### 2. Generate New Migration
```bash
# After making changes to models in src/models.py
make migrate MSG="Add new field to artifacts table"
```

### 3. Apply Migrations
```bash
make upgrade
```

### 4. View Migration History
```bash
make history
```

## Available Commands

### Database Migration Commands

| Command | Description | Example |
|---------|-------------|---------|
| `make migrate` | Generate new migration from model changes | `make migrate MSG="Add user table"` |
| `make migrate-manual` | Generate empty migration for manual changes | `make migrate-manual MSG="Custom data migration"` |
| `make upgrade` | Apply pending migrations | `make upgrade` |
| `make downgrade` | Rollback last migration | `make downgrade` |
| `make current` | Show current migration version | `make current` |
| `make history` | Show migration history | `make history` |
| `make reset-db` | Reset database (⚠️ destroys all data) | `make reset-db` |

### Development Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make test` | Run tests |
| `make run` | Run FastAPI development server |
| `make dev` | Run development server with auto-reload |
| `make clean` | Clean up temporary files |
| `make prod-run` | Run production server |

### Utility Commands

| Command | Description |
|---------|-------------|
| `make check-db` | Check database connection and show info |
| `make show-tables` | Show database tables (SQLite only) |

## Workflow Examples

### Adding a New Model

1. **Add the model** to `src/models.py`:
```python
class NewModel(Base):
    __tablename__ = 'new_models'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Generate migration**:
```bash
make migrate MSG="Add new_models table"
```

3. **Apply migration**:
```bash
make upgrade
```

4. **Verify**:
```bash
make current
make show-tables
```

### Modifying an Existing Model

1. **Modify the model** in `src/models.py`:
```python
class Artifact(Base):
    # ... existing fields ...
    
    # Add new field
    priority = Column(Integer, default=0)
    
    # Modify existing field
    status = Column(String(50), nullable=False, default='pending')
```

2. **Generate migration**:
```bash
make migrate MSG="Add priority field and modify status field"
```

3. **Apply migration**:
```bash
make upgrade
```

### Rolling Back Changes

If you need to undo the last migration:

```bash
make downgrade
```

⚠️ **Warning**: This will remove the changes from the database. Make sure you have backups if needed.

## Environment Configuration

### Database URL Configuration

The system reads the database URL from the `DATABASE_URL` environment variable:

```bash
# SQLite (default)
export DATABASE_URL="sqlite:///./integrityx.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/integrityx"

# MySQL
export DATABASE_URL="mysql://user:password@localhost:3306/integrityx"
```

### Environment Files

Create a `.env` file in the backend directory:

```bash
# Copy the example
cp .env.example .env

# Edit with your values
nano .env
```

Example `.env` content:
```env
DATABASE_URL=sqlite:///./integrityx.db
WALACOR_HOST=13.220.225.175
WALACOR_USERNAME=Admin
WALACOR_PASSWORD=Th!51s1T@gMu
```

## File Structure

```
backend/
├── alembic/                    # Alembic configuration
│   ├── versions/              # Migration files
│   │   └── 207bc87ea655_initial_migration.py
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
├── alembic.ini                # Alembic configuration file
├── Makefile                   # Convenient commands
├── src/
│   └── models.py              # SQLAlchemy models
└── integrityx.db              # SQLite database (created by migrations)
```

## Migration Files

Migration files are stored in `alembic/versions/` and follow this naming pattern:
```
{revision_id}_{description}.py
```

Example: `207bc87ea655_initial_migration.py`

Each migration file contains:
- **Revision ID**: Unique identifier for the migration
- **Upgrade function**: Applies the migration
- **Downgrade function**: Rolls back the migration
- **Dependencies**: Links to previous migrations

## Best Practices

### 1. Always Review Generated Migrations
```bash
# Generate migration
make migrate MSG="Add user table"

# Review the generated file
cat alembic/versions/*_add_user_table.py

# Apply only after review
make upgrade
```

### 2. Use Descriptive Migration Messages
```bash
# Good
make migrate MSG="Add email field to users table"

# Bad
make migrate MSG="fix"
```

### 3. Test Migrations in Development First
```bash
# Test the migration
make upgrade

# Verify the changes
make show-tables
make current
```

### 4. Backup Before Major Changes
```bash
# Create backup
cp integrityx.db integrityx.db.backup

# Apply migration
make upgrade

# If something goes wrong, restore
cp integrityx.db.backup integrityx.db
```

### 5. Use Manual Migrations for Data Changes
```bash
# For schema changes (automatic)
make migrate MSG="Add new column"

# For data migrations (manual)
make migrate-manual MSG="Migrate existing data"
# Then edit the generated file to add data migration logic
```

## Troubleshooting

### Common Issues

#### 1. "Target database is not up to date"
```bash
# Check current status
make current

# Apply pending migrations
make upgrade
```

#### 2. "Can't locate revision identified by 'xyz'"
```bash
# Check migration history
make history

# Reset database if needed (⚠️ destroys data)
make reset-db
```

#### 3. "Table already exists"
```bash
# Check if migration was already applied
make current

# If needed, mark as applied without running
alembic stamp head
```

#### 4. Import Errors in Migration Files
```bash
# Make sure models are properly imported in env.py
# Check that src.models is in Python path
```

### Getting Help

```bash
# Show all available commands
make help

# Get Alembic help
alembic --help

# Check Alembic version
alembic --version
```

## Production Deployment

### 1. Set Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### 2. Apply Migrations
```bash
make upgrade
```

### 3. Verify
```bash
make current
```

### 4. Start Application
```bash
make prod-run
```

## Security Notes

- ⚠️ Never commit `.env` files with real credentials
- ✅ Use `.env.example` for documentation
- ✅ Use environment variables in production
- ✅ Backup database before major migrations
- ✅ Test migrations in staging environment first

## Integration with FastAPI

The FastAPI application automatically uses the same database configuration:

```python
# In main_simple.py
from src.database import Database

# Database will use DATABASE_URL environment variable
db = Database()
```

This ensures that the application and migrations use the same database connection.


