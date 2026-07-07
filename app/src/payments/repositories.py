import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RabbitQueuesEnum
from src.core.exceptions import InternalServerError
from src.outbox.repositories import OutboxRepository
from src.payments.enums import PaymentStatusEnum
from src.payments.exceptions import PaymentCollisionError
from src.payments.models import PaymentModel
from src.payments.schemas import PaymentOutboxMessageSchema, PaymentRequestSchema

logger = logging.getLogger(__name__)


class PaymentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def add_payment(self, payment: PaymentRequestSchema) -> PaymentModel | None:
        try:  # noqa: PLW0717
            payment_model = PaymentModel(
                **payment.model_dump(),
            )
            self._db.add(payment_model)

            await self._db.flush([payment_model])

            outbox_repository = OutboxRepository(self._db)
            await outbox_repository.add_outbox_message_to_session(
                payment_model.idempotency_key,
                PaymentOutboxMessageSchema.model_validate(payment_model).model_dump(),
                RabbitQueuesEnum.PAYMENT_NEW,
            )

            await self._db.commit()

            logger.info(
                "Successfully created payment",
                extra={"payment_id": str(payment_model.id)},
            )

        except PaymentCollisionError as e:
            logger.exception("Failed to generate unique code for offer")
            raise InternalServerError from e
        except Exception as e:
            await self._db.rollback()
            logger.exception("Failed to create payment.")
            raise InternalServerError from e

        return payment_model

    async def get_payment_by_id(self, id_: UUID) -> PaymentModel | None:
        result = await self._db.execute(
            sa.select(PaymentModel).where(
                PaymentModel.id == id_,
                PaymentModel.is_deleted.is_(False),
            ),
        )

        return result.scalar_one_or_none()

    async def update_payment_status_by_id(self, payment_id: UUID, status: PaymentStatusEnum) -> PaymentModel:
        payment = await self._db.get(PaymentModel, payment_id)

        if payment is None:
            raise InternalServerError

        payment.status = status
        await self._db.commit()
        await self._db.refresh(payment)

        return payment
