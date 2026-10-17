"""FastAPI dependencies and authentication."""

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> bool:
    """Simple API Key authentication. Allows anonymous access if enabled."""
    if settings.allow_anonymous:
        return True

    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
        )
    return True
