"""Response header middleware for API versioning and Verity debugging."""

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import config


class ApiHeadersMiddleware(BaseHTTPMiddleware):
    """Attach service identity headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-AIHawk-Service"] = "aihawk"
        response.headers["X-AIHawk-Version"] = config.API_VERSION
        response.headers["X-AIHawk-Provider"] = config.LLM_MODEL_TYPE
        return response
