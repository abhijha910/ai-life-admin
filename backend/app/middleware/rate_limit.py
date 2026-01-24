"""Rate limiting middleware"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
import time
from app.config import settings

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request"""
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/api/health", "/api/docs", "/api/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier (IP address or user ID)
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self._check_rate_limit(client_id, request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, client_id: str, path: str) -> bool:
        """Check if client has exceeded rate limit"""
        # Different limits for different endpoints
        if path.startswith("/api/v1/auth"):
            limit = settings.RATE_LIMIT_PER_MINUTE
            window = 60  # 1 minute
        else:
            limit = settings.RATE_LIMIT_PER_HOUR
            window = 3600  # 1 hour
        
        key = f"rate_limit:{client_id}:{path}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        current_count = int(current)
        if current_count >= limit:
            return False
        
        redis_client.incr(key)
        return True
