"""Admin API router for authentication and configuration management."""

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
from anth2oai.configs import ConfigManager

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== 认证相关 ====================


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """登录并获取 JWT Token"""
    user = await User.filter(username=request.username).first()

    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token, expires = create_access_token(user.username)
    logger.info(f"用户 {user.username} 登录成功")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """获取当前用户信息"""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ==================== 用户管理 ====================


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """修改当前用户密码"""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if not user.verify_password(request.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误",
        )

    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码至少需要6个字符",
        )

    await user.set_password(request.new_password)
    logger.info(f"用户 {user.username} 修改了密码")

    return {"message": "密码修改成功"}


@router.post("/change-username")
async def change_username(
    request: ChangeUsernameRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """修改当前用户名"""
    user = await User.filter(username=current_user.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误",
        )

    # 检查新用户名是否已被使用
    existing_user = await User.filter(username=request.new_username).first()
    if existing_user and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用",
        )

    if len(request.new_username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名至少需要3个字符",
        )

    old_username = user.username
    user.username = request.new_username
    await user.save()
    logger.info(f"用户 {old_username} 将用户名修改为 {request.new_username}")

    # 返回新的 Token
    token, _ = create_access_token(user.username)
    return {
        "message": "用户名修改成功",
        "access_token": token,
        "token_type": "bearer",
    }


# ==================== 配置管理 ====================


@router.get("/configs", response_model=list[ConfigResponse])
async def get_all_configs(current_user: TokenData = Depends(get_current_user)):
    """获取所有配置项"""
    configs = await Config.all()
    return [
        ConfigResponse(
            id=c.id,
            key=c.key,
            value=c.value,
            description=c.description,
            updated_at=c.updated_at,
        )
        for c in configs
    ]


@router.get("/configs/{key}", response_model=ConfigResponse)
async def get_config(key: str, current_user: TokenData = Depends(get_current_user)):
    """获取指定配置项"""
    config = await Config.filter(key=key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 '{key}' 不存在",
        )

    return ConfigResponse(
        id=config.id,
        key=config.key,
        value=config.value,
        description=config.description,
        updated_at=config.updated_at,
    )


@router.put("/configs/{key}")
async def update_config(
    key: str,
    request: ConfigUpdateRequest,
    current_user: TokenData = Depends(get_current_user),
):
    """更新配置项（持久化到数据库）"""
    config = await Config.filter(key=key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 '{key}' 不存在",
        )

    config.value = request.value
    await config.save()

    # Update ConfigManager cache
    await ConfigManager.set(key, request.value)

    logger.info(f"配置项 '{key}' 被 {current_user.username} 更新")

    return {"message": f"配置项 '{key}' 更新成功"}


@router.post("/configs/refresh")
async def refresh_configs(current_user: TokenData = Depends(get_current_user)):
    """刷新配置缓存（从数据库重新加载）"""
    await ConfigManager.refresh()
    logger.info(f"配置缓存已被 {current_user.username} 刷新")
    return {"message": "配置缓存已刷新"}
