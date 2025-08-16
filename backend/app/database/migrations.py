"""
Database migration utilities for Streamlink Dashboard
"""
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional
from .base import engine


async def run_migrations() -> bool:
    """
    Run database migrations programmatically
    
    Returns:
        bool: True if migrations were successful, False otherwise
    """
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent
        
        # Run alembic upgrade head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Database migrations completed successfully")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False


async def create_initial_migration() -> bool:
    """
    Create the initial migration for the database schema
    
    Returns:
        bool: True if migration creation was successful, False otherwise
    """
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent
        
        # Run alembic revision --autogenerate
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Initial migration created successfully")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration creation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration creation: {e}")
        return False


async def get_current_revision() -> Optional[str]:
    """
    Get the current database revision
    
    Returns:
        Optional[str]: Current revision ID or None if error
    """
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent
        
        # Run alembic current
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to get the revision ID
        output = result.stdout.strip()
        if output:
            # Extract revision ID from output (format: "revision_id (head)")
            revision_id = output.split()[0]
            return revision_id
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get current revision: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error getting current revision: {e}")
        return None


async def check_migrations_status() -> dict:
    """
    Check the status of database migrations
    
    Returns:
        dict: Status information including current revision and available migrations
    """
    try:
        # Get the backend directory path
        backend_dir = Path(__file__).parent.parent.parent
        
        # Run alembic history
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "history"],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        current_revision = await get_current_revision()
        
        return {
            "current_revision": current_revision,
            "history": result.stdout,
            "status": "success"
        }
        
    except subprocess.CalledProcessError as e:
        return {
            "current_revision": None,
            "history": None,
            "error": str(e),
            "status": "error"
        }
    except Exception as e:
        return {
            "current_revision": None,
            "history": None,
            "error": str(e),
            "status": "error"
        }


if __name__ == "__main__":
    # Test the migration utilities
    async def test_migrations():
        print("Testing migration utilities...")
        
        # Check current status
        status = await check_migrations_status()
        print(f"Current status: {status}")
        
        # Create initial migration if needed
        if not status.get("current_revision"):
            print("Creating initial migration...")
            success = await create_initial_migration()
            if success:
                print("Running migrations...")
                await run_migrations()
        
        print("Migration test completed!")
    
    asyncio.run(test_migrations())
