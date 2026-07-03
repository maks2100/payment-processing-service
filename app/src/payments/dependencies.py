import typing as t

from fastapi import Depends as Depends


from src.core.dependencies import AsyncDbSessionDI, HttpClientDI
from src.payments.repositories import PaymentRepository
from src.payments.services import PaymentService


async def get_payment_repository(
    session: AsyncDbSessionDI,
) -> PaymentRepository:
    return PaymentRepository(session)


PaymentRepositoryDI = t.Annotated[PaymentRepository, Depends(get_payment_repository)]


async def get_payment_service(
    repository: PaymentRepositoryDI,
    client: HttpClientDI,
) -> PaymentService:
    return PaymentService(repository, client)


PaymentServiceDI = t.Annotated[PaymentService, Depends(get_payment_service)]
