"""Security middleware — rate limiting, CORS hardening, request size limits."""
import os
import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    WINDOW_SECONDS = 60
    MAX_REQUESTS = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

    def __init__(self, app):
        super().__init__(app)
        self._counts: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.WINDOW_SECONDS
        self._counts[ip] = [t for t in self._counts[ip] if t > window_start]
        if len(self._counts[ip]) >= self.MAX_REQUESTS:
            return JSONResponse(
                {"ok": False, "error": "rate_limit_exceeded", "retry_after": self.WINDOW_SECONDS},
                status_code=429,
                headers={"Retry-After": str(self.WINDOW_SECONDS)},
            )
        self._counts[ip].append(now)
        return await call_next(request)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    MAX_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(1 * 1024 * 1024)))

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_BYTES:
            return JSONResponse({"ok": False, "error": "request_too_large"}, status_code=413)
        return await call_next(request)


def get_cors_origins() -> list:
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw or raw.strip() == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]
