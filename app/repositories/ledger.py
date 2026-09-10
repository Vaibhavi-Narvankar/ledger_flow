from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import LedgerEntry


class LedgerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        entry: LedgerEntry,
    ) -> LedgerEntry:
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)

        return entry

    async def get_by_transaction_id(
        self,
        transaction_id: int,
    ) -> list[LedgerEntry]:
        result = await self.db.execute(
            select(LedgerEntry)
            .where(
                LedgerEntry.transaction_id == transaction_id
            )
            .order_by(LedgerEntry.id)
        )

        return list(result.scalars().all())