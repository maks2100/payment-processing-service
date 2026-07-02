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


class PaymentPayloadSchema(PaymentBaseSchema):
    ...


class PaymentRequestSchema(PaymentBaseSchema):
    idempotency_key: str


class PaymentResponseSchema(PaymentBaseSchema):
    id: UUID
    idempotency_key: str
    status: PaymentStatusEnum
    metadata_: dict | list | None = Field(
        serialization_alias="metadata",
        default_factory=dict
    )
