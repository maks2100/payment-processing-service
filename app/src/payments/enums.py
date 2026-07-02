from enum import StrEnum


class PaymentStatusEnum(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class CurrencyEnum(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class RabbitQueuesEnum(StrEnum):
    PAYMENT_NEW = "payment.new"
    PAYMENT_DLQ = "payment_dlq"
