from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Transaction | None:
        result = await self.db.execute(
            select(Transaction).where(
                Transaction.idempotency_key == idempotency_key
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        transaction: Transaction,
    ) -> Transaction:
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)

        return transaction