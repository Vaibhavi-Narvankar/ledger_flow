from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import UserAlreadyExistsError,InsufficientBalanceError,SameWalletTransferError,CurrencyMismatchError


async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": str(exc),
        },
    )

async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

async def wallet_already_exists_handler(
    request: Request,
    exc: WalletAlreadyExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )

async def wallet_not_found_handler(
    request: Request,
    exc: WalletNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

async def unsupported_currency_handler(
    request: Request,
    exc: UnsupportedCurrencyError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},

    )

async def insufficient_balance_handler(
    request: Request,
    exc: InsufficientBalanceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

async def same_wallet_transfer_handler(
    request: Request,
    exc: SameWalletTransferError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

async def currency_mismatch_handler(
    request: Request,
    exc: CurrencyMismatchError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )