import logging

from src.core.broker.rabbit import PAYMENT_DLQ_QUEUE, PAYMENT_EXCHANGE, PAYMENT_NEW_QUEUE, router as rabbit_router
from src.core.dependencies import RabbitBrokerDI
from src.core.enums import RabbitQueuesEnum
from src.outbox.dependencies import HandledEventServiceDI
from src.payments.dependencies import PaymentServiceDI
from src.payments.schemas import PaymentStorageSchema

logger = logging.getLogger(__name__)


@rabbit_router.subscriber(PAYMENT_NEW_QUEUE, PAYMENT_EXCHANGE)
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


@rabbit_router.subscriber(PAYMENT_DLQ_QUEUE)
async def handle_dlq_message(
    payment: PaymentStorageSchema,
) -> None:
    logger.error(f"Error DLQ payment: {payment.idempotency_key}")
