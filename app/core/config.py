from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "CampusConnect API"
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # DigitalOcean Spaces
    DIGITAL_OCEAN_SPACES_ACCESS_KEY: str
    DIGITAL_OCEAN_SPACES_SECRET_KEY: str
    DIGITAL_OCEAN_SPACES_ENDPOINT: str
    DIGITAL_OCEAN_SPACES_BUCKET: str
    DIGITAL_OCEAN_SPACES_REGION: str
    IMAGE_CDN_BASE_URL: str

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        return os.getenv("TESTING") == "true"

    class Config:
        # Check if running in test mode and use appropriate env file
        env_file = ".env.test" if os.getenv("TESTING") == "true" else ".env"
        extra = "ignore"


settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """Validate that all critical settings are configured"""
    # Skip validation in test mode
    if os.getenv("TESTING") == "true":
        return

    required_fields = [
        "DATABASE_URL",
        "SECRET_KEY",
        "STRIPE_SECRET_KEY",
        "DIGITAL_OCEAN_SPACES_ACCESS_KEY",
    ]

    missing = []
    for field in required_fields:
        if not getattr(settings, field, None):
            missing.append(field)

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    # Warn about debug mode in production
    if settings.is_production and settings.DEBUG:
        import logging

        logging.warning("⚠️  DEBUG mode is enabled in production!")


# Run validation only if not testing
validate_settings()
