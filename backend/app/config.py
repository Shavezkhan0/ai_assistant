from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # LLM Settings
    groq_api_key: str
    model_provider: str = "groq"
    
    # Database Settings
    database_url: str
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    # Optional: Direct connection string for test scripts
    postgres_connection_string: str | None = None
    
    # Redis Settings
    use_redis: bool = False
    
    # ChromaDB Settings
    chroma_persist_dir: str = "./data/chroma_db"
    
    # App Settings
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Fix the model_ namespace warning
        protected_namespaces = ('settings_',)
        # Allow extra fields
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()