import logging

from src.core.broker.rabbit import router as rabbit_router
from src.outbox.dependencies import HandledEventServiceDI
from src.payments.dependencies import PaymentServiceDI
from src.payments.enums import RabbitQueuesEnum
from src.payments.schemas import PaymentStorageSchema

logger = logging.getLogger(__name__)


@rabbit_router.subscriber(RabbitQueuesEnum.PAYMENT_NEW)
async def handle_message(
    payment: PaymentStorageSchema,
    payment_service: PaymentServiceDI,
    handled_event_service: HandledEventServiceDI,
    ) -> None:
    logger.info(f"Received message: {payment}")

    handled_event = await handled_event_service.get_event_by_idempotency_id(payment.idempotency_key)
    if handled_event:
        logger.debug(f"Payment {payment.idempotency_key} already handled")
        return

    await payment_service.handled_payment(payment)

    await handled_event_service.create_event(payment.idempotency_key)

    logger.info(f"Payment {payment.idempotency_key} success handled")
