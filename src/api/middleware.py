"""HTTP middleware for the AIHawk API."""

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log inbound API requests for debugging Verity and external integrations."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response
