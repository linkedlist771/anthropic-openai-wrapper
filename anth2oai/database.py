"""Database initialization and connection management."""

import os
import asyncio
from tortoise import Tortoise
from loguru import logger
from anth2oai.models import User, Config, DEFAULT_CONFIGS

# Global flag to track if DB is initialized (for multi-worker scenarios)
_db_initialized = False
_init_lock = asyncio.Lock()


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": os.environ.get("DATABASE_PATH", "data/admin.db"),
            },
        },
    },
    "apps": {
        "models": {
            "models": ["anth2oai.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize database connection and create tables."""
    global _db_initialized

    async with _init_lock:
        if _db_initialized:
            return

        db_path = os.environ.get("DATABASE_PATH", "data/admin.db")

        # Ensure directory exists
        os.makedirs(
            os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True
        )

        await Tortoise.init(
            db_url=f"sqlite://{db_path}",
            modules={"models": ["anth2oai.models"]},
        )
        await Tortoise.generate_schemas(safe=True)

        # Create default admin user if not exists
        try:
            admin_exists = await User.filter(username="admin").exists()
            if not admin_exists:
                await User.create(
                    username="admin",
                    password_hash=User.hash_password("admin123"),
                )
                logger.info("创建默认管理员用户 (admin/admin123)")
        except Exception as e:
            logger.warning(f"创建管理员用户时出错（可能已存在）: {e}")

        # Create or update default configs
        for key, config_data in DEFAULT_CONFIGS.items():
            try:
                config = await Config.filter(key=key).first()
                if not config:
                    # Try to get from environment first
                    env_value = os.environ.get(key, config_data["value"])
                    await Config.create(
                        key=key,
                        value=env_value,
                        description=config_data["description"],
                    )
                    logger.info(f"创建默认配置: {key}")
                else:
                    # Update description if changed (for i18n updates)
                    if config.description != config_data["description"]:
                        config.description = config_data["description"]
                        await config.save()
                        logger.info(f"更新配置描述: {key}")
            except Exception as e:
                logger.warning(f"处理配置 {key} 时出错: {e}")

        # Remove configs that are no longer in DEFAULT_CONFIGS
        try:
            all_configs = await Config.all()
            for config in all_configs:
                if config.key not in DEFAULT_CONFIGS:
                    await config.delete()
                    logger.info(f"删除废弃配置: {config.key}")
        except Exception as e:
            logger.warning(f"清理废弃配置时出错: {e}")

        _db_initialized = True
        logger.info("数据库初始化完成")


async def close_db():
    """Close database connections."""
    global _db_initialized
    await Tortoise.close_connections()
    _db_initialized = False


async def get_config_dict() -> dict:
    """Get all configurations as a dictionary."""
    configs = await Config.all()
    return {c.key: c.value for c in configs}
