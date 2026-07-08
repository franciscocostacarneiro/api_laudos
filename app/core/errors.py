"""Custom exceptions and a shared FastAPI exception handler.

All error responses follow a single consistent shape:

    {
      "error": {
        "code": "machine_readable_code",
        "message": "Human readable summary",
        "details": [ { "field": "...", "message": "...", "code": "..." } ]
      }
    }

This matches the conventions described in the api-and-interface-design skill.
"""
from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class APIError(Exception):
    """Base class for all API-level errors.

    Carries an HTTP status, a machine-readable code, a human message and
    optional field-level details.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(APIError):
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            status_code=404,
            code="not_found",
            message=f"{resource} '{identifier}' was not found.",
        )


class ValidationError_(APIError):
    def __init__(self, message: str, details: list[dict] | None = None) -> None:
        super().__init__(status_code=422, code="validation_error", message=message, details=details)


def _build_error_body(
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_body(exc.code, exc.message, exc.details),
    )


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    # Translate FastAPI's validation errors into our consistent shape.
    details = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        details.append(
            {
                "field": loc or None,
                "message": err.get("msg", "Invalid value"),
                "code": err.get("type", "invalid"),
            }
        )
    return JSONResponse(
        status_code=422,
        content=_build_error_body(
            "validation_error", "Request validation failed.", details
        ),
    )


async def pydantic_validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        details.append(
            {
                "field": loc or None,
                "message": err.get("msg", "Invalid value"),
                "code": err.get("type", "invalid"),
            }
        )
    return JSONResponse(
        status_code=422,
        content=_build_error_body(
            "validation_error", "Response validation failed.", details
        ),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    # Never leak internal details — return a generic 500.
    return JSONResponse(
        status_code=500,
        content=_build_error_body("internal_error", "An unexpected error occurred."),
    )


def register_exception_handlers(app) -> None:  # type: ignore[no-untyped-def]
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
