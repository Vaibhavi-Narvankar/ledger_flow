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

    async def get_wallet_transactions(
            self,
            wallet_id: int,
            transaction_type: str | None = None,
            status: str | None = None,
            currency: str | None = None,
            start_date=None,
            end_date=None,
            offset: int = 0,
            limit: int = 20,
        ) -> list[Transaction]:
            query = select(Transaction).where(
                or_(
                    Transaction.sender_wallet_id == wallet_id,
                    Transaction.receiver_wallet_id == wallet_id,
                )
            )
            if transaction_type is not None:
                query = query.where(
                    Transaction.transaction_type == transaction_type
                )
            if status is not None:
                query = query.where(
                    Transaction.status == status
                )
            if currency is not None:
                query = query.where(
                    Transaction.currency == currency
                )
            if start_date is not None:
                query = query.where(
                    Transaction.created_at >= start_date
                )

            if end_date is not None:
                query = query.where(
                    Transaction.created_at <= end_date
                )
            query = (
                query
                .order_by(
                    Transaction.created_at.desc(),
                    Transaction.id.desc(),
                )
                .offset(offset)
                .limit(limit)
            )
            result = await self.db.execute(query)
            return list(result.scalars().all())
    async def count_wallet_transactions(
            self,
            wallet_id: int,
            transaction_type: str | None = None,
            status: str | None = None,
            currency: str | None = None,
            start_date=None,
            end_date=None,
        ) -> int:
            query = select(
                func.count(Transaction.id)
            ).where(
                or_(
                    Transaction.sender_wallet_id == wallet_id,
                    Transaction.receiver_wallet_id == wallet_id,
                )
            )
            if transaction_type is not None:
                query = query.where(
                    Transaction.transaction_type == transaction_type
                )
            if status is not None:
                query = query.where(
                    Transaction.status == status
                )
            if currency is not None:
                query = query.where(
                    Transaction.currency == currency
                )
            if start_date is not None:
                query = query.where(
                    Transaction.created_at >= start_date
                )
            if end_date is not None:
                query = query.where(
                    Transaction.created_at <= end_date
                )
            result = await self.db.execute(query)
            return result.scalar_one()