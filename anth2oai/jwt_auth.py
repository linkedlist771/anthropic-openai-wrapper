"""JWT Authentication module for admin panel."""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from loguru import logger

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.environ.get("JWT_EXPIRATION_HOURS", "24"))

security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data."""

    username: str
    exp: datetime


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response without password."""

    id: int
    username: str
    created_at: datetime
    updated_at: datetime


def create_access_token(username: str) -> tuple[str, datetime]:
    """Create a JWT access token."""
    expires = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "username": username,
        "exp": expires,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenData(
            username=payload["username"],
            exp=datetime.fromtimestamp(payload["exp"]),
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Token 已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"无效的 Token: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """获取当前已认证的用户"""
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


class ChangePasswordRequest(BaseModel):
    """Change password request body."""

    current_password: str
    new_password: str


class ChangeUsernameRequest(BaseModel):
    """Change username request body."""

    new_username: str
    password: str  # Current password for verification


class ConfigUpdateRequest(BaseModel):
    """Config update request body."""

    value: str


class ConfigResponse(BaseModel):
    """Config response."""

    id: int
    key: str
    value: str
    description: Optional[str]
    updated_at: datetime
