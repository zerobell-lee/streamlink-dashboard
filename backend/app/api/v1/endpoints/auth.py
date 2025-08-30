"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import hashlib
import secrets

from app.database.database import get_db
from app.database.models import User
from app.core.config import settings
from app.core.jwt import create_user_token, blacklist_token, clear_user_tokens, get_current_user_from_token

router = APIRouter()
security = HTTPBasic()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class MessageResponse(BaseModel):
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with Basic Auth credentials and receive JWT token
    """
    # Get user from database first
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    
    # If user exists, verify against database password
    if user:
        password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
        if user.password_hash == password_hash and user.is_active:
            # Update last login
            from datetime import datetime, timezone
            user.last_login = datetime.now()
            await db.commit()
            
            # Create JWT token
            access_token = create_user_token(
                user_id=user.id,
                username=user.username,
                is_admin=user.is_admin
            )
            
            return LoginResponse(
                access_token=access_token,
                token_type="bearer",
                user={
                    "id": user.id,
                    "username": user.username,
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
            )
    
    # If no user exists and credentials match default admin, create user
    elif (credentials.username == settings.BASIC_AUTH_USERNAME and 
          credentials.password == settings.BASIC_AUTH_PASSWORD):
        
        # Create admin user with default password
        password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
        user = User(
            username=credentials.username,
            password_hash=password_hash,
            is_admin=True,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Update last login
        from datetime import datetime, timezone
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        
        # Create JWT token
        access_token = create_user_token(
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "username": user.username,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    authorization: Optional[str] = Header(None)
):
    """
    Logout by blacklisting current JWT token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required"
        )
    
    token = authorization.split(" ")[1]
    success = blacklist_token(token)
    
    if success:
        return MessageResponse(message="Successfully logged out")
    else:
        return MessageResponse(message="Invalid token")


@router.put("/password", response_model=MessageResponse)
async def change_password(
    request: PasswordChangeRequest,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password (requires current password verification)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required"
        )
    
    token = authorization.split(" ")[1]
    user_info = get_current_user_from_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_info["user_id"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    current_password_hash = hashlib.sha256(request.current_password.encode()).hexdigest()
    if user.password_hash != current_password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    new_password_hash = hashlib.sha256(request.new_password.encode()).hexdigest()
    user.password_hash = new_password_hash
    await db.commit()
    
    # Clear all tokens for this user (force re-login)
    cleared_count = clear_user_tokens(user.id)
    
    return MessageResponse(
        message=f"Password changed successfully. {cleared_count} active sessions terminated."
    )


@router.get("/verify", response_model=dict)
async def verify_token(
    authorization: Optional[str] = Header(None)
):
    """
    Verify JWT token and return user info
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required"
        )
    
    token = authorization.split(" ")[1]
    user_info = get_current_user_from_token(token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "user": user_info
    }