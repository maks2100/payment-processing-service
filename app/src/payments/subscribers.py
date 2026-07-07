import asyncio
import logging

from src.core.broker.rabbit import PAYMENT_DLQ_QUEUE, PAYMENT_EXCHANGE, PAYMENT_NEW_QUEUE
from src.core.broker.rabbit import router as rabbit_router
from src.core.config import get_settings
from src.outbox.dependencies import HandledEventServiceDI
from src.payments.dependencies import PaymentServiceDI
from src.payments.schemas import PaymentStorageSchema

logger = logging.getLogger(__name__)

settings = get_settings()
if settings.include_consumer:

    @rabbit_router.subscriber(PAYMENT_NEW_QUEUE, PAYMENT_EXCHANGE)
    async def handle_message(
        payment: PaymentStorageSchema,
        payment_service: PaymentServiceDI,
        handled_event_service: HandledEventServiceDI,
        ) -> None:
        settings = get_settings()
        if not settings.include_consumer:
            return

        logger.info("Received message: %s", payment)

        handled_event = await handled_event_service.get_event_by_idempotency_id(payment.idempotency_key)
        if handled_event:
            logger.debug("Payment %s already handled", payment.idempotency_key)
            return

        await payment_service.handled_payment(payment)

        await handled_event_service.create_event(payment.idempotency_key)

        logger.info("Payment %s success handled", payment.idempotency_key)

    @rabbit_router.subscriber(PAYMENT_DLQ_QUEUE)
    async def handle_dlq_message(
        payment: PaymentStorageSchema,
    ) -> None:
        logger.error("Error DLQ payment: %s", payment.idempotency_key)
        await asyncio.sleep(1)
