import typing as t

from fastapi import Depends

from src.core.dependencies import AsyncDbSessionDI
from src.outbox.repositories import HandledEventRepository
from src.outbox.services import HandledEventService


def get_handled_event_repository(
    session: AsyncDbSessionDI,
) -> HandledEventRepository:
    return HandledEventRepository(session)


HandledEventRepositoryDI = t.Annotated[HandledEventRepository, Depends(get_handled_event_repository)]


def get_handled_event_service(
    repository: HandledEventRepositoryDI,
) -> HandledEventService:
    return HandledEventService(repository)


HandledEventServiceDI = t.Annotated[HandledEventService, Depends(get_handled_event_service)]
