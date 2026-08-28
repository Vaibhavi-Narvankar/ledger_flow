from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class WalletRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, wallet_id: int) -> Wallet | None:
        result = await self.db.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )

        return result.scalar_one_or_none()

    async def get_by_user_and_currency(
        self,
        user_id: int,
        currency: str,
    ) -> Wallet | None:
        result = await self.db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.currency == currency,
            )
        )

        return result.scalar_one_or_none()

    async def create(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)

        await self.db.flush()
        await self.db.refresh(wallet)

        return wallet