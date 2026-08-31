from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import SUPPORTED_CURRENCIES
from app.core.exceptions import (
    UnsupportedCurrencyError,
    UserNotFoundError,
    WalletAlreadyExistsError,
)
from app.models.wallet import Wallet
from app.repositories.user import UserRepository
from app.repositories.wallet import WalletRepository
from app.schemas.wallet import WalletCreate, WalletResponse
from app.core.exceptions import WalletNotFoundError


class WalletService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.wallet_repository = WalletRepository(db)
        self.user_repository = UserRepository(db)

    async def create_wallet(
        self,
        data: WalletCreate,
    ) -> WalletResponse:
        currency = data.currency.strip().upper()

        if currency not in SUPPORTED_CURRENCIES:
            raise UnsupportedCurrencyError(
                f"Unsupported currency: {currency}"
            )

        user = await self.user_repository.get_by_id(data.user_id)

        if user is None:
            raise UserNotFoundError(
                "User does not exist"
            )

        existing_wallet = (
            await self.wallet_repository.get_by_user_and_currency(
                data.user_id,
                currency,
            )
        )

        if existing_wallet is not None:
            raise WalletAlreadyExistsError(
                "Wallet already exists for this currency"
            )

        wallet = Wallet(
            user_id=data.user_id,
            currency=currency,
        )

        try:
            wallet = await self.wallet_repository.create(wallet)
            await self.db.commit()

        except IntegrityError as exc:
            await self.db.rollback()

            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise WalletAlreadyExistsError(
                    "Wallet already exists for this currency"
                ) from None

            raise

        return WalletResponse.model_validate(wallet)

    async def get_wallet(self, wallet_id: int) -> Wallet:

        wallet = await self.wallet_repository.get_by_id(wallet_id)

        if wallet is None:

            raise WalletNotFoundError(

                f"Wallet {wallet_id} not found"

            )

        return wallet

    async def get_user_wallets(self, user_id: int) -> list[Wallet]:

        return await self.wallet_repository.get_by_user_id(user_id)

    async def delete_wallet(self, wallet_id: int) -> None:

        wallet = await self.wallet_repository.get_by_id(wallet_id)

        if wallet is None:

            raise WalletNotFoundError(

                f"Wallet {wallet_id} not found"

            )

        await self.wallet_repository.delete(wallet)