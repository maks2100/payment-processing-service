import logging

from src.outbox.repositories import HandledEventRepository
from src.outbox.schemas import HandledEventSchema

logger = logging.getLogger(__name__)


class HandledEventService:
    def __init__(self, repository: HandledEventRepository) -> None:
        self._repository = repository

    async def create_event(self, idempotency_key: str) -> HandledEventSchema | None:
        created = await self._repository.add(HandledEventSchema.model_validate({"idempotency_key": idempotency_key}))
        return HandledEventSchema.model_validate(created)

    async def get_event_by_idempotency_id(self, idempotency_id: str) -> HandledEventSchema | None:
        event = await self._repository.get_event_by_idempotency_key(idempotency_id)
        if not event:
            return None
        return HandledEventSchema.model_validate(event)
