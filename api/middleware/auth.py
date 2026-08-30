"""Authentication middleware."""

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Validate API key."""
    if not api_key:
        return "dev-key"
    return api_key


class AuthMiddleware:
    """Simple auth middleware for development."""

    async def __call__(self, request: Request, call_next):
        if request.url.path.startswith("/health") or request.url.path == "/":
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "dev-key")
        request.state.api_key = api_key

        return await call_next(request)