"""Admin API router for authentication and configuration management."""

import os
from fastapi import APIRouter, HTTPException, Depends, status
from loguru import logger
from anth2oai.models import User, Config
from anth2oai.jwt_auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest,
    ChangeUsernameRequest,
    ConfigUpdateRequest,
    ConfigResponse,
    TokenData,
    create_access_token,
    get_current_user,
    JWT_EXPIRATION_HOURS,
)
from anth2oai.database import sync_configs_to_env

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== Authentication ====================

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login and get JWT token."""
    user = await User.filter(username=request.username).first()
    
    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    token, expires = create_access_token(user.username)
    logger.info(f"User {user.username} logged in successfully")
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information."""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ==================== User Management ====================

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """Change current user's password."""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.verify_password(request.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    
    await user.set_password(request.new_password)
    logger.info(f"User {user.username} changed password")
    
    return {"message": "Password changed successfully"}


@router.post("/change-username")
async def change_username(
    request: ChangeUsernameRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """Change current user's username."""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )
    
    # Check if new username is already taken
    existing_user = await User.filter(username=request.new_username).first()
    if existing_user and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    if len(request.new_username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters",
        )
    
    old_username = user.username
    user.username = request.new_username
    await user.save()
    logger.info(f"User {old_username} changed username to {request.new_username}")
    
    # Return new token with new username
    token, _ = create_access_token(user.username)
    return {
        "message": "Username changed successfully",
        "access_token": token,
        "token_type": "bearer",
    }


# ==================== Configuration Management ====================

@router.get("/configs", response_model=list[ConfigResponse])
async def get_all_configs(current_user: TokenData = Depends(get_current_user)):
    """Get all configuration settings."""
    configs = await Config.all()
    return [
        ConfigResponse(
            id=c.id,
            key=c.key,
            value=c.value if c.key != "ANTHROPIC_API_KEY" and c.key != "API_KEY" else mask_secret(c.value),
            description=c.description,
            updated_at=c.updated_at,
        )
        for c in configs
    ]


@router.get("/configs/{key}", response_model=ConfigResponse)
async def get_config(key: str, current_user: TokenData = Depends(get_current_user)):
    """Get a specific configuration setting."""
    config = await Config.filter(key=key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{key}' not found",
        )
    
    return ConfigResponse(
        id=config.id,
        key=config.key,
        value=config.value if config.key != "ANTHROPIC_API_KEY" and config.key != "API_KEY" else mask_secret(config.value),
        description=config.description,
        updated_at=config.updated_at,
    )


@router.put("/configs/{key}")
async def update_config(
    key: str,
    request: ConfigUpdateRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """Update a configuration setting."""
    config = await Config.filter(key=key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config '{key}' not found",
        )
    
    config.value = request.value
    await config.save()
    
    # Sync to environment
    os.environ[key] = request.value
    
    logger.info(f"Config '{key}' updated by {current_user.username}")
    
    return {"message": f"Config '{key}' updated successfully"}


@router.post("/configs/sync")
async def sync_configs(current_user: TokenData = Depends(get_current_user)):
    """Sync all database configs to environment variables."""
    await sync_configs_to_env()
    logger.info(f"Configs synced to environment by {current_user.username}")
    return {"message": "Configs synced to environment successfully"}


def mask_secret(value: str) -> str:
    """Mask sensitive values for display."""
    if not value or len(value) < 8:
        return "*" * len(value) if value else ""
    return value[:4] + "*" * (len(value) - 8) + value[-4:]

