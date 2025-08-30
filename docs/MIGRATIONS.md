# Database Migrations Guide

This document describes how to work with database migrations in the Streamlink Dashboard project.

## Overview

The project uses Alembic for database migrations with SQLAlchemy 2.0+ and async support. All migrations are stored in the `alembic/versions/` directory.

## Migration Commands

### Initial Setup

1. **Create initial migration** (first time only):
   ```bash
   cd backend
   python -m alembic revision --autogenerate -m "Initial migration"
   ```

2. **Run migrations**:
   ```bash
   python -m alembic upgrade head
   ```

### Development Workflow

1. **Create a new migration**:
   ```bash
   python -m alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**:
   ```bash
   python -m alembic upgrade head
   ```

3. **Rollback migrations**:
   ```bash
   python -m alembic downgrade -1  # Rollback one step
   python -m alembic downgrade base  # Rollback to beginning
   ```

4. **Check migration status**:
   ```bash
   python -m alembic current  # Show current revision
   python -m alembic history  # Show migration history
   python -m alembic show <revision>  # Show specific revision
   ```

## Programmatic Migration

You can also run migrations programmatically using the utilities in `app/database/migrations.py`:

```python
from app.database.migrations import run_migrations, create_initial_migration

# Run all pending migrations
await run_migrations()

# Create initial migration
await create_initial_migration()
```

## Migration Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** on a copy of production data
3. **Use descriptive migration messages**
4. **Keep migrations small and focused**
5. **Test both upgrade and downgrade operations**

## Migration Structure

Each migration file contains:
- `upgrade()`: Apply the migration
- `downgrade()`: Rollback the migration
- Metadata about the migration (revision ID, dependencies, etc.)

## Troubleshooting

### Common Issues

1. **Migration conflicts**: Resolve by editing the migration file manually
2. **Missing dependencies**: Ensure all models are imported in `env.py`
3. **Database locked**: Close all database connections before running migrations

### Recovery

If migrations fail:
1. Check the error message
2. Manually fix the migration file if needed
3. Run `alembic upgrade head` again
4. If still failing, consider rolling back and recreating the migration

## Environment Variables

The database URL is configured in `alembic.ini`:
```ini
sqlalchemy.url = sqlite+aiosqlite:///./streamlink_dashboard.db
```

For production, you can override this with environment variables.

## Testing Migrations

Test migrations using the provided utilities:
```bash
cd backend
python app/database/migrations.py
```

This will:
1. Check current migration status
2. Create initial migration if needed
3. Run all pending migrations
4. Report success or failure
