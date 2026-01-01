"""Database models for admin panel using Tortoise ORM."""

from tortoise import fields, models
import bcrypt


class User(models.Model):
    """Admin user model for authentication."""

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password_hash = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storage."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    async def set_password(self, password: str) -> None:
        """Set a new password."""
        self.password_hash = self.hash_password(password)
        await self.save()


class Config(models.Model):
    """Configuration settings model."""

    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=100, unique=True)
    value = fields.TextField()
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "configs"

    @classmethod
    async def get_value(cls, key: str, default: str = "") -> str:
        """Get a config value by key."""
        config = await cls.filter(key=key).first()
        return config.value if config else default

    @classmethod
    async def set_value(cls, key: str, value: str, description: str = None) -> "Config":
        """Set a config value."""
        config, _ = await cls.update_or_create(
            key=key, defaults={"value": value, "description": description}
        )
        return config


# Default configuration keys
DEFAULT_CONFIGS = {
    "ANTHROPIC_API_KEY": {
        "value": "",
        "description": "Anthropic API Key for Claude models",
    },
    "ANTHROPIC_BASE_URL": {
        "value": "https://api.anthropic.com/v1",
        "description": "Anthropic API Base URL",
    },
    "DEFAULT_MAX_TOKENS": {
        "value": "40960",
        "description": "Default maximum tokens for API responses",
    },
    "API_KEY": {
        "value": "",
        "description": "API Key for accessing this service (leave empty to disable auth)",
    },
    "LOG_LEVEL": {
        "value": "INFO",
        "description": "Logging level (DEBUG, INFO, WARNING, ERROR)",
    },
    "RATE_LIMIT": {
        "value": "100",
        "description": "Rate limit per minute (requests)",
    },
}
