"""Error handling middleware"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import structlog

logger = structlog.get_logger()


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    error_str = str(exc)
    logger.error("Database error", error=error_str, path=request.url.path)
    
    # Check if it's a connection error
    if "Connect call failed" in error_str or "could not connect" in error_str.lower():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database connection failed",
                "message": "PostgreSQL database is not running. Please start PostgreSQL to use this feature.",
                "help": "Run 'docker compose up -d postgres' or start PostgreSQL locally."
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "message": "An internal error occurred. Please try again later."
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    import traceback
    from app.config import settings
    
    error_str = str(exc)
    error_traceback = traceback.format_exc()
    logger.error("Unhandled exception", error=error_str, path=request.url.path, exc_info=True)
    
    # In development, include more details
    error_detail = error_str if settings.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": error_detail,
            "message": "An unexpected error occurred. Please try again later."
        }
    )


def setup_error_handlers(app):
    """Setup error handlers for the application"""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
