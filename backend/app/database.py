"""Database connection and session management"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Async engine for FastAPI
# Note: asyncpg doesn't connect immediately - connection is lazy
# The engine will only connect when actually used
# Disable pool_pre_ping to prevent connection attempt during import
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=False,  # Disable to prevent connection attempt during import
    pool_size=10,
    max_overflow=20,
    # asyncpg connection args (connection is lazy, won't hang on import)
    connect_args={
        "server_settings": {
            "application_name": "ai_life_admin",
        },
        "command_timeout": 5,  # 5 second timeout for queries
    },
)

# Sync engine for Alembic migrations
# Disable pool_pre_ping during import to prevent hanging if DB is not available
# Connection will only happen when actually used
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_pre_ping=False,  # Disable to prevent connection attempt during import
    pool_size=10,
    max_overflow=20,
    connect_args={
        "connect_timeout": 5,  # 5 second timeout for connection attempts
    },
    # Make connection truly lazy - don't connect until first use
    poolclass=None,  # Use default pool, but don't pre-connect
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Dependency for getting sync database session (for migrations)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
