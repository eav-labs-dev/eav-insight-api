"""Application-wide error handlers."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.error import build_error_response

STATUS_TO_ERROR_CODE = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "validation_error",
}


def _normalize_http_detail(detail: Any, status_code: int) -> tuple[str, str, list[dict[str, Any]]]:
    """Convert FastAPI/Starlette HTTP details into the EAV error shape."""
    fallback_code = STATUS_TO_ERROR_CODE.get(status_code, "http_error")

    if isinstance(detail, dict):
        code = str(detail.get("code") or fallback_code)
        message = str(detail.get("message") or detail.get("detail") or "Request failed.")
        raw_details = detail.get("details")
        details = raw_details if isinstance(raw_details, list) else []
        return code, message, details

    if isinstance(detail, str):
        return fallback_code, detail, []

    return fallback_code, "Request failed.", []


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Render HTTP exceptions with the standard API error response."""
    code, message, details = _normalize_http_detail(exc.detail, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_response(code=code, message=message, details=details),
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Render request validation errors with field-level details."""
    details = []
    for error in exc.errors():
        location = error.get("loc", ())
        field = ".".join(str(part) for part in location) if location else None
        details.append(
            {
                "field": field,
                "message": str(error.get("msg", "Invalid value.")),
                "type": str(error.get("type", "value_error")),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=build_error_response(
            code="validation_error",
            message="Request validation failed.",
            details=details,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-level exception handlers."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
