import asyncio
import logging

import sqlalchemy as sa

from src.core.broker.rabbit import broker as rabbit_broker
from src.core.db.manager import async_db_manager
from src.outbox.enums import OutboxStatusEnum
from src.outbox.models import OutboxMessageModel

logger = logging.getLogger(__name__)


async def relay_loop(poll_interval: float = 1.0, batch_size: int = 20):
    async with rabbit_broker:
        while True:
            await asyncio.sleep(poll_interval)
            try:
                await process_batch(batch_size)
            except Exception:
                logger.exception("Relay task failed")


async def process_batch(batch_size: int):
    async with async_db_manager.session() as session:
        result = await session.execute(
            sa.select(OutboxMessageModel)
            .where(OutboxMessageModel.status == OutboxStatusEnum.PENDING)
            .order_by(OutboxMessageModel.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        messages = result.scalars().all()

        for msg in messages:
            try:
                await rabbit_broker.publish(
                    msg.payload,
                    queue=msg.queue,                )
                msg.status = OutboxStatusEnum.SENT
            except Exception:
                logger.exception("Send to queue failed")
                msg.status = OutboxStatusEnum.FAILED
        try:
            await session.commit()
        except Exception:
            logger.exception("Unknown error")
