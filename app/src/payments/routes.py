import typing as t
from uuid import UUID

from fastapi import APIRouter, HTTPException, Header, status

from src.payments.enums import RabbitQueuesEnum
from src.core.dependencies import RabbitBrokerDI
from src.core.exceptions import NotFoundError
from src.core.responses import SuccessResponse
from src.payments.dependencies import PaymentServiceDI
from src.payments.schemas import PaymentPayloadSchema, PaymentRequestSchema

api_router = APIRouter()


@api_router.post(
    "/payments",
    summary="Creating payment data",
)
async def create_payment(
    payment: PaymentPayloadSchema,
    idempotency_key: t.Annotated[str, Header()], 
    payment_service: PaymentServiceDI,
    rabbit_broker: RabbitBrokerDI,
) -> SuccessResponse:
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is missing."
        )

    validated_request = PaymentRequestSchema(
        idempotency_key=idempotency_key,
        **payment.model_dump()
    )

    storaged_payment = await payment_service.create_payment(validated_request)

    await rabbit_broker.publish(storaged_payment, RabbitQueuesEnum.PAYMENT_NEW)

    return SuccessResponse(
        data={},
        message="payments.created",
    )


@api_router.get(
    "/payments/{payment_id}",
    description="Getting payment data",
)
async def get_payment(
    payment_id: UUID,
    payment_service: PaymentServiceDI,
) -> SuccessResponse:
    data = await payment_service.get_payment_by_id(payment_id)
    if not data:
        raise NotFoundError
    return SuccessResponse(
        data=data,
        message="payments.created",
    )
