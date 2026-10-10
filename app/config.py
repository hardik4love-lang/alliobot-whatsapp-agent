from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "production"
    APP_PORT: int = 8000
    SECRET_KEY: str = "alliobot_default_secret_key"

    # Database & Redis
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/alliobot_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Evolution API
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str = "alliobot_secret_foss_api_key_2026"
    EVOLUTION_INSTANCE_NAME: str = "alliobot_primary_instance"

    # User & Single-Number Settings
    USER_PHONE_NUMBER: str = "+919876543210"
    OPERATIONS_GROUP_JID: str = "120363028475918234@g.us"

    # Anti-Ban Outbound Bounds (for single number safety)
    MAX_OUTBOUND_PER_DAY: int = 25
    MIN_OUTBOUND_INTERVAL_SECONDS: int = 180
    MAX_OUTBOUND_INTERVAL_SECONDS: int = 420
    CIRCUIT_BREAKER_BLOCK_THRESHOLD: float = 0.02

    # LLM Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q4_K_M"

    # Business Defaults
    DEFAULT_PRICE_PER_KG: float = 120.0
    BULK_DISCOUNT_PRICE_PER_KG: float = 110.0
    BULK_DISCOUNT_MIN_KG: float = 12.0
    DEFAULT_CITY: str = "Surat"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
