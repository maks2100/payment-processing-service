from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import APIError
from src.core.responses import ErrorDetail, ErrorResponse


async def api_exception_handler(_request: Request, exc: APIError) -> JSONResponse:  # noqa: RUF029
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.error.model_dump(),
        headers=exc.headers,
    )


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:  # noqa: RUF029
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", str(exc))

    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            success=False,
            errors=[ErrorDetail(code=f"HTTP_{status_code}", message=detail)],
        ).model_dump(),
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:  # noqa: RUF029
    errors: list[ErrorDetail] = []

    for err in exc.errors():
        field_parts = [str(part) for part in err.get("loc", ()) if part != "body"]
        errors.append(
            ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(err["msg"]),
                field=".".join(field_parts) if field_parts else None,
            ),
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ErrorResponse(
            success=False,
            errors=errors,
        ).model_dump(),
    )


async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:  # noqa: RUF029
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            errors=[
                ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="error.internal_contact_support",
                ),
            ],
        ).model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
