import asyncio
import logging
import random
from uuid import UUID

from src.core.clients import ClientProtocol
from src.payments.enums import PaymentStatusEnum
from src.payments.repositories import PaymentRepository
from src.payments.schemas import PaymentRequestSchema, PaymentStorageSchema

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self, repository: PaymentRepository, client: ClientProtocol) -> None:
        self._repository = repository
        self._client = client

    async def create_payment(self, payment_: PaymentRequestSchema) -> PaymentStorageSchema | None:
        payment = await self._repository.add_payment(payment_)
        if not payment:
            return
        return PaymentStorageSchema.model_validate(payment)

    async def get_payment_by_id(self, id_: UUID) -> PaymentStorageSchema | None:
        payment = await self._repository.get_payment_by_id(id_)
        if not payment:
            return
        return PaymentStorageSchema.model_validate(payment)

    async def handled_payment(self, payment: PaymentStorageSchema) -> None:
        delay = random.randrange(2, 6)

        await asyncio.sleep(delay)

        is_error = random.choices([0, 1], weights=[10, 90])[0]

        if not is_error:
            logger.debug("Success event")
            status = PaymentStatusEnum.SUCCEEDED
        else:
            logger.debug("Wrong event")
            status = PaymentStatusEnum.FAILED

        updated_payment = await self._repository.update_payment_status_by_id(payment.id, status)

        await self._client.send(str(payment.webhook_url), payment.model_dump(exclude={"webhook_url"}))

        logger.debug(f"Updated payment {updated_payment.id} with status {updated_payment.status}")
