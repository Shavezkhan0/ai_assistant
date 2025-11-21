from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings
from urllib.parse import quote_plus

settings = get_settings()

def get_database_url():
    """Get database URL from settings"""
    # Prefer full connection string if available
    if settings.database_url:
        # Normalize SQLAlchemy format (postgresql+psycopg:// -> postgresql://)
        # SQLAlchemy can handle both, but we normalize for consistency
        db_url = settings.database_url
        if db_url.startswith("postgresql+psycopg://"):
            db_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)
        return db_url
    
    # Otherwise, build from individual parameters
    if all([settings.postgres_host, settings.postgres_user, 
            settings.postgres_password, settings.postgres_db]):
        # URL-encode password for special characters
        encoded_password = quote_plus(settings.postgres_password)
        return f"postgresql://{settings.postgres_user}:{encoded_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}?sslmode=require"
    
    raise ValueError("Database connection parameters not properly configured")

# Get database URL
DATABASE_URL = get_database_url()

# Create engine with connection pooling
# SQLAlchemy handles postgresql+psycopg:// format correctly
# Use original database_url if it exists (may have postgresql+psycopg://)
db_url_for_engine = settings.database_url if hasattr(settings, 'database_url') and settings.database_url and settings.database_url.startswith("postgresql+psycopg://") else DATABASE_URL

engine = create_engine(
    db_url_for_engine,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Additional connections if needed
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI routes
def get_db():
    """Dependency that provides a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test connection on import
def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"⚠️  Database connection warning: {e}")
        return False