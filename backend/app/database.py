"""Database connection and session management"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.config import settings

# Base class for models - safe to import, no connection needed
Base = declarative_base()

# Engines and session factories - created lazily on first use
_async_engine = None
_sync_engine = None
_AsyncSessionLocal = None
_SessionLocal = None

def get_async_engine():
    """Get async engine (lazy initialization)"""
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=False,
            pool_size=10,
            max_overflow=20,
            connect_args={
                "server_settings": {
                    "application_name": "ai_life_admin",
                },
                "command_timeout": 5,
            },
        )
    return _async_engine

def get_sync_engine():
    """Get sync engine (lazy initialization)"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = create_engine(
            settings.DATABASE_URL_SYNC,
            echo=settings.DEBUG,
            pool_pre_ping=False,
            pool_size=10,
            max_overflow=20,
            connect_args={
                "connect_timeout": 5,
            },
        )
    return _sync_engine

def get_async_session_local():
    """Get async session factory (lazy initialization)"""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            get_async_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal

def get_session_local():
    """Get sync session factory (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_sync_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _SessionLocal

# For backward compatibility - use __getattr__ for module-level access
def __getattr__(name):
    if name == "async_engine":
        return get_async_engine()
    elif name == "sync_engine":
        return get_sync_engine()
    elif name == "AsyncSessionLocal":
        return get_async_session_local()
    elif name == "SessionLocal":
        return get_session_local()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    session_factory = get_async_session_local()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """Dependency for getting sync database session (for migrations)"""
    session_factory = get_session_local()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
