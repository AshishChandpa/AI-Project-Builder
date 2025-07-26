import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = None):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get user ID from auth header
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                # Extract user info from token (simplified)
                return f"user:{auth_header[-10:]}"  # Last 10 chars as identifier
            except:
                pass

        # Fallback to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        return f"ip:{request.client.host}"

    def _clean_old_requests(self, request_times: Deque[float]):
        """Remove requests older than 1 minute"""
        current_time = time.time()
        while request_times and current_time - request_times[0] > 60:
            request_times.popleft()

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting"""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc"]:
            return await call_next(request)

        client_id = self._get_client_id(request)
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(self.requests[client_id])

        # Check rate limit
        if len(self.requests[client_id]) >= self.calls_per_minute:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        self.requests[client_id].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.calls_per_minute - len(self.requests[client_id]))
        )
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

        return response
