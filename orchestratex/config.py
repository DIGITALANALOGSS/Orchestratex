from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Orchestratex"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./orchestratex.db"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # OpenAI settings
    OPENAI_API_KEY: str = ""
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # Password settings
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 100
    PASSWORD_REQUIREMENTS: str = "uppercase,lowercase,number,special"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
