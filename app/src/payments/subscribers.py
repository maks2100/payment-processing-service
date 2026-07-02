import logging

from src.core.broker.rabbit import router as rabbit_router
from src.payments.dependencies import PaymentServiceDI
from src.payments.enums import RabbitQueuesEnum
from src.payments.schemas import PaymentStorageSchema

logger = logging.getLogger(__name__)


@rabbit_router.subscriber(RabbitQueuesEnum.PAYMENT_NEW)
async def handle_message(
    payment_request: PaymentStorageSchema,
    payment_service: PaymentServiceDI,
    ) -> None:
    logger.info(f"Received message: {payment_request}")

    await payment_service.handled_payment(payment_request)
