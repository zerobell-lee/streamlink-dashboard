"""
JWT token handling utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
import secrets
from typing import Set

from app.core.config import settings

# In-memory token blacklist (for demo - use Redis in production)
_token_blacklist: Set[str] = set()

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    to_encode.update({"jti": secrets.token_urlsafe(32)})  # JWT ID for blacklisting
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload if valid
    """
    try:
        # Check if token is blacklisted
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        
        if jti and jti in _token_blacklist:
            return None
            
        return payload
        
    except JWTError:
        return None


def blacklist_token(token: str) -> bool:
    """
    Add token to blacklist (for logout/password change)
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        
        if jti:
            _token_blacklist.add(jti)
            return True
            
    except JWTError:
        pass
    
    return False


def clear_user_tokens(user_id: int) -> int:
    """
    Clear all tokens for a specific user (for password change)
    This is a simplified implementation - in production you'd store user_id with jti
    """
    # For now, just clear all tokens (since we don't track user_id per token)
    # In production, maintain a mapping of user_id -> [jti] 
    cleared_count = len(_token_blacklist)
    _token_blacklist.clear()
    return cleared_count


def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract user information from valid token
    """
    payload = verify_token(token)
    if not payload:
        return None
    
    # Extract user info from token payload
    user_id = payload.get("sub")
    username = payload.get("username") 
    is_admin = payload.get("is_admin", False)
    
    if not user_id:
        return None
        
    return {
        "user_id": int(user_id),
        "username": username,
        "is_admin": is_admin
    }


def create_user_token(user_id: int, username: str, is_admin: bool = False) -> str:
    """
    Create JWT token for a specific user
    """
    token_data = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
        "iat": datetime.now()
    }
    
    return create_access_token(token_data)