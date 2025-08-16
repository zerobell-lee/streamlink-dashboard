"""
Authentication module for Basic Auth
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from typing import Optional

from app.database.database import get_db
from app.database.models import User
from app.core.config import settings


security = HTTPBasic()


async def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate user with Basic Auth
    """
    # For now, use simple username/password check
    # Later can be extended to use database
    if (credentials.username == settings.BASIC_AUTH_USERNAME and 
        credentials.password == settings.BASIC_AUTH_PASSWORD):
        
        # Get or create admin user
        result = await db.execute(
            select(User).where(User.username == credentials.username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create admin user if not exists
            user = User(
                username=credentials.username,
                password_hash="",  # Not used for Basic Auth
                is_admin=True,
                is_active=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


async def get_current_user(
    current_user: User = Depends(authenticate_user)
) -> User:
    """
    Get current authenticated user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated admin user
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    """
    # For Basic Auth, we don't use password hashing
    # This is for future JWT implementation
    return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    """
    Hash password
    """
    # For Basic Auth, we don't hash passwords
    # This is for future JWT implementation
    return password
