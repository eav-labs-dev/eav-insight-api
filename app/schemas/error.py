"""Standard API error response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Optional detail item for validation or field-level errors."""

    field: str | None = None
    message: str
    type: str | None = None


class ErrorPayload(BaseModel):
    """Machine-readable API error payload."""

    code: str = Field(min_length=2)
    message: str = Field(min_length=1)
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Top-level API error response wrapper."""

    error: ErrorPayload


def build_error_response(
    *,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a serializable API error response body."""
    return ErrorResponse(
        error=ErrorPayload(
            code=code,
            message=message,
            details=[ErrorDetail(**detail) for detail in details or []],
        )
    ).model_dump(mode="json")
