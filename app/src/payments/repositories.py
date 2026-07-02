import logging
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InternalServerError
from src.payments.exceptions import PaymentCollisionError
from src.payments.models import PaymentModel
from src.payments.schemas import PaymentIncomingSchema

logger = logging.getLogger(__name__)

class PaymentRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def add_payment(self, payment: PaymentIncomingSchema) -> PaymentModel | None:
        try:
            payment_model = PaymentModel(
                **payment.model_dump(),
            )
            self._db.add(payment_model)
            await self._db.commit()
            await self._db.refresh(payment_model)

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
