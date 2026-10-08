from fastapi import FastAPI
from app.middleware.database import database_failure_middleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    WalletAlreadyExistsError,
    WalletNotFoundError,
    UnsupportedCurrencyError,
    InsufficientBalanceError,
    SameWalletTransferError,
    CurrencyMismatchError,
    IdempotencyConflictError,
    TransactionNotFoundError,
    RedisUnavailableError,
)
from app.core.exception_handlers import (
    user_already_exists_handler,
    user_not_found_handler,
    wallet_already_exists_handler,
    wallet_not_found_handler,
    unsupported_currency_handler,
    insufficient_balance_handler,
    same_wallet_transfer_handler,
    currency_mismatch_handler,
    idempotency_conflict_handler,
    transaction_not_found_handler,
    redis_unavailable_handler,


)
from contextlib import asynccontextmanager
from app.core.redis import create_redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = create_redis_client()
    try:
        yield
    finally:
        await app.state.redis.aclose()



settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    version="1.0.0",
    debug=settings.debug,
)
app.middleware("http")(database_failure_middleware)

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
)

app.add_exception_handler(
    CurrencyMismatchError,
    currency_mismatch_handler,
)

app.add_exception_handler(
    IdempotencyConflictError,
    idempotency_conflict_handler,
)

app.add_exception_handler(
    TransactionNotFoundError,
    transaction_not_found_handler,
)

app.add_exception_handler(
    UserNotFoundError,
    user_not_found_handler,
)

app.add_exception_handler(
    WalletAlreadyExistsError,
    wallet_already_exists_handler,
)

app.add_exception_handler(
    WalletNotFoundError,
    wallet_not_found_handler,
)

app.add_exception_handler(
    UnsupportedCurrencyError,
    unsupported_currency_handler,
)

app.add_exception_handler(
    RedisUnavailableError,
    redis_unavailable_handler,
)


app.include_router(
    api_router,
    prefix="/api/v1",
)
