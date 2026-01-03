"""Configuration management module.

All configurations are read from the database (Config model).
Initial values are loaded from .env file when the config doesn't exist in DB.
Web interface modifications update the database directly.
"""

import os
from typing import Optional
from loguru import logger

# Legacy constants for backward compatibility (used by client.py as a standalone library)
DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
DEFAULT_MAX_TOKENS = 40960

# Default configuration values (used when not in .env and not in DB)
DEFAULT_VALUES = {
    "ANTHROPIC_BASE_URL": DEFAULT_ANTHROPIC_BASE_URL,
    "DEFAULT_MAX_TOKENS": str(DEFAULT_MAX_TOKENS),
    "API_KEY": "",
    "LOG_LEVEL": "INFO",
}


class ConfigManager:
    """
    Configuration manager that reads from database.

    Priority order:
    1. Database value (if exists)
    2. Environment variable (as initial value when creating DB record)
    3. Default value from DEFAULT_VALUES
    """

    _instance: Optional["ConfigManager"] = None
    _cache: dict[str, str] = {}
    _initialized: bool = False

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls) -> None:
        """Initialize the config manager by loading all configs from DB."""
        instance = cls()
        await instance._load_from_db()
        cls._initialized = True
        logger.info("ConfigManager initialized")

    async def _load_from_db(self) -> None:
        """Load all configurations from database into cache."""
        from anth2oai.models import Config

        configs = await Config.all()
        self._cache = {c.key: c.value for c in configs}
        logger.debug(f"Loaded {len(self._cache)} configs from database")

    @classmethod
    async def get(cls, key: str, default: Optional[str] = None) -> str:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if not found (falls back to DEFAULT_VALUES)

        Returns:
            Configuration value as string
        """
        instance = cls()

        # If we have it in cache, return it
        if key in instance._cache:
            return instance._cache[key]

        # Try to get from database
        from anth2oai.models import Config

        config = await Config.filter(key=key).first()

        if config:
            instance._cache[key] = config.value
            return config.value

        # Fall back to default
        if default is not None:
            return default
        return DEFAULT_VALUES.get(key, "")

    @classmethod
    async def get_int(cls, key: str, default: int = 0) -> int:
        """Get a configuration value as integer."""
        value = await cls.get(key)
        try:
            return int(value) if value else default
        except ValueError:
            logger.warning(
                f"Config {key} value '{value}' is not a valid integer, using default {default}"
            )
            return default

    @classmethod
    async def set(cls, key: str, value: str) -> None:
        """
        Set a configuration value (updates database and cache).

        Args:
            key: Configuration key
            value: New value
        """
        from anth2oai.models import Config

        config = await Config.filter(key=key).first()
        if config:
            config.value = value
            await config.save()
        else:
            # This shouldn't happen normally, but handle it
            from anth2oai.models import DEFAULT_CONFIGS

            desc = DEFAULT_CONFIGS.get(key, {}).get("description", "")
            await Config.create(key=key, value=value, description=desc)

        # Update cache
        instance = cls()
        instance._cache[key] = value
        logger.info(f"Config '{key}' updated")

    @classmethod
    async def refresh(cls) -> None:
        """Refresh cache from database."""
        instance = cls()
        await instance._load_from_db()
        logger.info("Config cache refreshed")

    @classmethod
    async def get_all(cls) -> dict[str, str]:
        """Get all configuration values as a dictionary."""
        instance = cls()

        # Ensure we have fresh data
        if not instance._cache:
            await instance._load_from_db()

        return dict(instance._cache)

    @classmethod
    def get_cached(cls, key: str, default: Optional[str] = None) -> str:
        """
        Get a configuration value from cache (synchronous).
        Use this only when you're sure the config is already cached.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value as string
        """
        instance = cls()
        if key in instance._cache:
            return instance._cache[key]
        if default is not None:
            return default
        return DEFAULT_VALUES.get(key, "")

    @classmethod
    def get_cached_int(cls, key: str, default: int = 0) -> int:
        """Get a cached configuration value as integer (synchronous)."""
        value = cls.get_cached(key)
        try:
            return int(value) if value else default
        except ValueError:
            return default


# Convenience functions for common configs
async def get_anthropic_base_url() -> str:
    """Get the Anthropic API base URL."""
    return await ConfigManager.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")


async def get_default_max_tokens() -> int:
    """Get the default max tokens value."""
    return await ConfigManager.get_int("DEFAULT_MAX_TOKENS", 40960)


async def get_api_key() -> str:
    """Get the API key for this service (for authentication)."""
    return await ConfigManager.get("API_KEY")


async def get_log_level() -> str:
    """Get the log level."""
    return await ConfigManager.get("LOG_LEVEL", "INFO")
