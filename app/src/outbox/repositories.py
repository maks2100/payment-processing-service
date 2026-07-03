import logging

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from src.outbox.models import HandledEventModel, OutboxMessageModel
from src.outbox.schemas import HandledEventSchema
from src.payments.enums import RabbitQueuesEnum

logger = logging.getLogger(__name__)


class OutboxRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def add_outbox_message_to_session(
            self,
            idempotency_key: str,
            payload: dict,
            queue: RabbitQueuesEnum,
    ) -> AsyncSession | None:

        message = OutboxMessageModel(
            queue=queue,
            idempotency_key=idempotency_key,
            payload={
                **payload,
            },
        )

        self._db.add(message)

        return self._db

    async def get_outbox_message_by_idempotency_key(self, idempotency_key: str) -> OutboxMessageModel | None:
        try:
            result = await self._db.execute(
                sa.select(OutboxMessageModel).where(
                    OutboxMessageModel.idempotency_key == idempotency_key,
                    OutboxMessageModel.is_deleted.is_(False),
                ),
            )
        except Exception:
            logger.exception("Error with getting outbox message")
            return

        return result.scalar_one_or_none()


class HandledEventRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def add(
        self,
        event: HandledEventSchema
    ) -> HandledEventModel | None:
        try:
            event_model = HandledEventModel(
                **event.model_dump()
            )

            self._db.add(event_model)

            await self._db.commit()
            await self._db.refresh(event_model)
        except Exception:
            logger.exception("Error with adding event")
            await self._db.rollback()
            raise
        
        return event_model

    async def get_event_by_idempotency_key(self, idempotency_key: str) -> HandledEventModel | None:
        result = await self._db.execute(
            sa.select(HandledEventModel).where(
                HandledEventModel.idempotency_key == idempotency_key,
                HandledEventModel.is_deleted.is_(False),
            ),
        )

        return result.scalar_one_or_none()
