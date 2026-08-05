"""Simple in-memory rate limiting for expensive AIHawk API routes."""

import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

import config


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit POSTs to document-generation endpoints per client IP."""

    PROTECTED_PREFIXES = (
        "/api/v1/resume",
        "/api/v1/cover-letter",
    )

    def __init__(self, app):
        super().__init__(app)
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def _is_protected(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.PROTECTED_PREFIXES)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _allow(self, key: str) -> bool:
        now = time.time()
        window = float(config.RATE_LIMIT_WINDOW_SECONDS)
        limit = int(config.RATE_LIMIT_REQUESTS)
        bucket = self._hits[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method == "POST" and self._is_protected(request.url.path):
            key = self._client_key(request)
            if not self._allow(key):
                return JSONResponse(
                    status_code=429,
                    content={
                        "status": "error",
                        "detail": (
                            f"Rate limit exceeded: max {config.RATE_LIMIT_REQUESTS} "
                            f"requests per {config.RATE_LIMIT_WINDOW_SECONDS}s"
                        ),
                    },
                    headers={
                        "Retry-After": str(config.RATE_LIMIT_WINDOW_SECONDS),
                    },
                )
        return await call_next(request)
