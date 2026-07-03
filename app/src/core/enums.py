from enum import StrEnum


class Environment(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PRODUCTION = "production"


class RabbitQueuesEnum(StrEnum):
    PAYMENT_NEW = "payment.new"
    PAYMENT_DLQ = "payment.dlq"
