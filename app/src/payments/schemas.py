from decimal import Decimal
import typing as t
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, condecimal, field_serializer

from src.payments.enums import CurrencyEnum, PaymentStatusEnum


class PaymentBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount:  t.Annotated[
        Decimal,
        condecimal(max_digits=12, decimal_places=2),
    ]
    currency: t.Annotated[
        CurrencyEnum,
        StringConstraints(strip_whitespace=True, min_length=3, max_length=3),
    ] = CurrencyEnum.RUB
    description: str
    metadata_: dict | list | None = Field(
        serialization_alias="metadata",
        alias="metadata",
        default_factory=dict
    )
    webhook_url: HttpUrl

    @field_serializer("webhook_url")
    def _webhook_url_to_str(self, value: HttpUrl) -> str:  # noqa: PLR6301
        return str(value)

    @field_serializer("amount")
    def _amount_to_str(self, value: Decimal) -> str:  # noqa: PLR6301
        return str(value)


class PaymentPayloadSchema(PaymentBaseSchema):
    ...


class PaymentRequestSchema(PaymentBaseSchema):
    idempotency_key: str


class PaymentStorageSchema(PaymentBaseSchema):
    id: UUID
    idempotency_key: str
    status: PaymentStatusEnum
    metadata_: dict | list | None = Field(
        serialization_alias="metadata",
        default_factory=dict
    )

class PaymentOutboxMessageSchema(PaymentStorageSchema):
    idempotency_key: str
    metadata_: dict | list | None = Field(
        serialization_alias="metadata",
        default_factory=dict
    )

    @field_serializer("id")
    def _id_to_str(self, value: UUID) -> str:  # noqa: PLR6301
        return str(value)
