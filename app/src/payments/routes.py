from uuid import UUID
from fastapi import APIRouter

from src.payments.dependencies import PaymentServiceDI
from src.core.exceptions import NotFoundError
from src.core.responses import SuccessResponse
from src.payments.schemas import PaymentIncomingSchema

api_router = APIRouter()


@api_router.post(
    "/payments",
    summary="Creating payment data",
)
async def create_payment(
    payment: PaymentIncomingSchema,
    payment_service: PaymentServiceDI
) -> SuccessResponse:
    return SuccessResponse(
        data=await payment_service.create_payment(payment),
        message="payments.created",
    )


@api_router.get(
    "/payments/{payment_id}",
    description="Getting payment data",
)
async def get_payment(
    payment_id: UUID,
    payment_service: PaymentServiceDI
) -> SuccessResponse:
    data = await payment_service.get_payment_by_id(payment_id)
    if not data:
        raise NotFoundError
    return SuccessResponse(
        data=data,
        message="payments.created",
    )
