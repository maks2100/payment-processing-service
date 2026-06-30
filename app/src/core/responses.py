from pydantic import BaseModel


class SuccessResponse[T](BaseModel):
    success: bool = True
    message: str | None = None
    data: T | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    errors: list[ErrorDetail]
    data: dict | None = None
    meta: dict | None = None
