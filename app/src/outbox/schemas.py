from pydantic import BaseModel


class HandledEventSchema(BaseModel):
    idempotency_key: str
