from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    # LLM Settings
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    model_provider: str = Field(default="groq", alias="MODEL_PROVIDER")
    
    # Database Settings
    database_url: str = Field(..., alias="DATABASE_URL")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    
    # Optional: Direct connection string for test scripts
    postgres_connection_string: str | None = Field(default=None, alias="POSTGRES_CONNECTION_STRING")
    
    # Redis Settings
    use_redis: bool = Field(default=False, alias="USE_REDIS")
    
    # ChromaDB Settings
    chroma_persist_dir: str = Field(default="./data/chroma_db", alias="CHROMA_PERSIST_DIR")
    
    # App Settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow",
        populate_by_name=True  # Allow both alias and field name
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()