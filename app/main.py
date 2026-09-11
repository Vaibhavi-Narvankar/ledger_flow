from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import UserAlreadyExistsError,CurrencyMismatchError
from app.core.exception_handlers import user_already_exists_handler


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)
app.add_exception_handler(
    UserAlreadyExistsError,
    user_already_exists_handler,

)
app.add_exception_handler(
    InsufficientBalanceError,
    insufficient_balance_handler,
)

app.add_exception_handler(
    SameWalletTransferError,
    same_wallet_transfer_handler,
    CurrencyMismatchError,
    currency_mismatch_handler,
)

app.include_router(
    api_router,
    prefix="/api/v1",
)