from enum import StrEnum


class OutboxStatusEnum(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
