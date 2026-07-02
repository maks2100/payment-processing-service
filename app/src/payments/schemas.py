from decimal import Decimal
import typing as t

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, condecimal, field_serializer

from src.payments.enums import CurrencyEnum, PaymentStatusEnum


class PaymentBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idempotency_key: str
    amount:  t.Annotated[
        Decimal,
        condecimal(max_digits=12, decimal_places=2),
    ]
    currency: t.Annotated[
        CurrencyEnum,
        StringConstraints(strip_whitespace=True, min_length=3, max_length=3),
    ] = CurrencyEnum.RUB
    description: str
    metadata_: dict | list | None = Field(serialization_alias="metadata")
    webhook_url: HttpUrl

    @field_serializer("webhook_url")
    def _webhook_url_to_str(self, value: HttpUrl) -> str:  # noqa: PLR6301
        return str(value)


class PaymentIncomingSchema(PaymentBaseSchema):
    ...


class PaymentResponseSchema(PaymentBaseSchema):
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
