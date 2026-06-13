from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AgriVision AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production-use-32-char-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://agrivision:agrivision_secret@localhost:5432/agrivision_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    # Storage
    UPLOAD_DIR: str = "/app/uploads"
    MODEL_DIR: str = "/app/ml_models"
    MAX_UPLOAD_SIZE_MB: int = 50

    # External APIs
    OPENWEATHER_API_KEY: str = "demo_key"
    SENTINEL_HUB_CLIENT_ID: str = ""
    SENTINEL_HUB_CLIENT_SECRET: str = ""

    # ML Settings
    BATCH_SIZE: int = 32
    IMAGE_SIZE: int = 224
    CNN_CONFIDENCE_THRESHOLD: float = 0.65

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
