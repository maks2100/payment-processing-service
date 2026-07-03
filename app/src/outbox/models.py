import datetime as dt

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base, IdMixin, TimestampMixin, IsDeletedMixin
from src.outbox.enums import OutboxStatusEnum


class OutboxMessageModel(Base, IdMixin, TimestampMixin, IsDeletedMixin):
    __tablename__ = "outbox_messages"

    idempotency_key: Mapped[str] = mapped_column(index=True, unique=True)
    queue: Mapped[str] = mapped_column(sa.String(255))
    payload: Mapped[dict] = mapped_column(sa.JSON)
    status: Mapped[OutboxStatusEnum] = mapped_column(
        sa.String(20),
        default=OutboxStatusEnum.PENDING
    )
    handled_at: Mapped[dt.datetime | None] = mapped_column(
        sa.DateTime,
        onupdate=sa.func.now(),
    )


class HandledEventModel(Base, IdMixin, TimestampMixin, IsDeletedMixin):
    __tablename__ = "handled_events"

    idempotency_key: Mapped[str] = mapped_column(index=True, unique=True)
