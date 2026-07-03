import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.payments.enums import CurrencyEnum, PaymentStatusEnum
from src.core.db.base import Base, IdMixin, TimestampMixin, IsDeletedMixin


class PaymentModel(Base, IdMixin, TimestampMixin, IsDeletedMixin):
    __tablename__ = "payments"

    idempotency_key: Mapped[str] = mapped_column(index=True, unique=True)
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(12, 2))
    currency: Mapped[CurrencyEnum] = mapped_column(
        sa.Enum(CurrencyEnum),
        default=CurrencyEnum.RUB,
    )
    description: Mapped[str | None]
    metadata_: Mapped[dict | list | None] = mapped_column(
        sa.JSON,
        default=lambda: {},
    )
    webhook_url: Mapped[str]
    handled_at: Mapped[dt.datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        onupdate=sa.func.now(),

    )
    status: Mapped[PaymentStatusEnum] = mapped_column(
        sa.Enum(PaymentStatusEnum),
        default=PaymentStatusEnum.PENDING,
    )
