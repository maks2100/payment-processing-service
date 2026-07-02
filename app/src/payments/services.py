from uuid import UUID

from src.payments.schemas import PaymentRequestSchema, PaymentResponseSchema
from src.payments.repositories import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self._repository = repository

    async def create_payment(self, payment_: PaymentRequestSchema) -> PaymentResponseSchema | None:
        payment = await self._repository.add_payment(payment_)
        if not payment:
            return
        return PaymentResponseSchema.model_validate(payment)

    async def get_payment_by_id(self, id_: UUID) -> PaymentResponseSchema | None:
        payment = await self._repository.get_payment_by_id(id_)
        if not payment:
            return
        return PaymentResponseSchema.model_validate(payment)
