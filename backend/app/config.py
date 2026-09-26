"""
Centralized application configuration.
Loaded from environment variables / .env file (12-factor app style).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "BlogSphere API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-this-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # Database
    DATABASE_URL: str = "sqlite:///./blogsphere.db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File uploads
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp,image/gif"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 50

    # Simple in-process cache TTL (seconds) for public listing endpoint
    CACHE_TTL_SECONDS: int = 30

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Insert sample users and posts when the database is empty.
    # Tests and a blank local database should set this to false.
    SEED_DEMO_DATA: bool = True

    # Optional model provider for post summaries. Blank keys use the local fallback.
    AI_PROVIDER: str = "anthropic"  # "anthropic" | "openai" | "none"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "claude-sonnet-4-6"
    AI_REQUEST_TIMEOUT_SECONDS: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_image_types_list(self) -> list[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
