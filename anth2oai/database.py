"""Database initialization and connection management."""

import os
from tortoise import Tortoise
from loguru import logger
from anth2oai.models import User, Config, DEFAULT_CONFIGS


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
    db_path = os.environ.get("DATABASE_PATH", "data/admin.db")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    
    await Tortoise.init(
        db_url=f"sqlite://{db_path}",
        modules={"models": ["anth2oai.models"]},
    )
    await Tortoise.generate_schemas()
    
    # Create default admin user if not exists
    admin_exists = await User.filter(username="admin").exists()
    if not admin_exists:
        await User.create(
            username="admin",
            password_hash=User.hash_password("admin123"),
        )
        logger.info("Created default admin user (admin/admin123)")
    
    # Create default configs from environment or defaults
    for key, config_data in DEFAULT_CONFIGS.items():
        config_exists = await Config.filter(key=key).exists()
        if not config_exists:
            # Try to get from environment first
            env_value = os.environ.get(key, config_data["value"])
            await Config.create(
                key=key,
                value=env_value,
                description=config_data["description"],
            )
            logger.info(f"Created default config: {key}")
    
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connections."""
    await Tortoise.close_connections()


async def get_config_dict() -> dict:
    """Get all configurations as a dictionary."""
    configs = await Config.all()
    return {c.key: c.value for c in configs}


async def sync_configs_to_env():
    """Sync database configs to environment variables."""
    configs = await Config.all()
    for config in configs:
        if config.value:  # Only set if not empty
            os.environ[config.key] = config.value

