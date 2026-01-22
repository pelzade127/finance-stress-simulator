"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stress_simulator"
    
    # Cost of Living API
    COL_API_BASE_URL: str = "http://localhost:3001"
    COL_API_TIMEOUT_SECONDS: int = 10
    COL_FALLBACK_PATH: str = "data/col_fallback.json"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Application
    APP_NAME: str = "Finance Stress Simulator"
    VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
