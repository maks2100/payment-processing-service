from fastapi import status

from src.core.responses import ErrorDetail, ErrorResponse


class APIError(Exception):
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        status_code: int,
        code: str,
        message: str,
        field: str | None = None,
        data: dict | None = None,
        meta: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.error = ErrorResponse(
            success=False,
            errors=[ErrorDetail(code=code, message=message, field=field)],
            data=data,
            meta=meta,
        )
        super().__init__(message)


class ForbiddenError(APIError):
    def __init__(
        self,
        message: str = "error.forbidden",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code=code,
            message=message,
        )


class NotFoundError(APIError):
    def __init__(
        self,
        message: str = "error.not_found",
        code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
            message=message,
        )


class ConflictError(APIError):
    def __init__(
        self,
        message: str = "error.conflict",
        code: str = "CONFLICT",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
        )


class InternalServerError(APIError):
    def __init__(
        self,
        message: str = "error.internal",
        code: str = "INTERNAL_SERVER_ERROR",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=code,
            message=message,
        )
