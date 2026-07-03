from pydantic import BaseModel, ConfigDict


class HandledEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idempotency_key: str
