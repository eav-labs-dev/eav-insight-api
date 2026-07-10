"""Reusable API exception helpers."""

from fastapi import HTTPException, status


def api_error(
    *,
    status_code: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> HTTPException:
    """Create an HTTPException using the standard error detail shape."""
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
        headers=headers,
    )


def bad_request(message: str) -> HTTPException:
    """Return a 400 API error."""
    return api_error(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="bad_request",
        message=message,
    )


def unauthorized(message: str = "Could not validate credentials.") -> HTTPException:
    """Return a 401 API error with the bearer challenge header."""
    return api_error(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="unauthorized",
        message=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(message: str) -> HTTPException:
    """Return a 403 API error."""
    return api_error(
        status_code=status.HTTP_403_FORBIDDEN,
        code="forbidden",
        message=message,
    )


def not_found(message: str) -> HTTPException:
    """Return a 404 API error."""
    return api_error(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        message=message,
    )


def conflict(message: str) -> HTTPException:
    """Return a 409 API error."""
    return api_error(
        status_code=status.HTTP_409_CONFLICT,
        code="conflict",
        message=message,
    )
