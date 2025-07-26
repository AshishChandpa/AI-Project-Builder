import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Cursor Clone Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database (Optional for now)
    DATABASE_URL: str = "sqlite+aiosqlite:///./cursor_clone.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis (Completely Optional)
    REDIS_URL: Optional[str] = None
    REDIS_ENABLED: bool = False  # Add explicit flag
    REDIS_POOL_SIZE: int = 10

    # AI Providers
    GEMINI_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None
    DEFAULT_AI_PROVIDER: str = "gemini"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    AI_RATE_LIMIT_PER_MINUTE: int = 30

    # File Storage
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c",
        ".go", ".rs", ".rb", ".php", ".html", ".css", ".sql", ".json",
        ".yaml", ".yml", ".md", ".txt", ".sh", ".dockerfile"
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @validator("REDIS_ENABLED", pre=True, always=True)
    def set_redis_enabled(cls, v, values):
        redis_url = values.get('REDIS_URL')
        if redis_url and redis_url.strip() and redis_url.startswith(('redis://', 'rediss://', 'unix://')):
            return True
        return False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
