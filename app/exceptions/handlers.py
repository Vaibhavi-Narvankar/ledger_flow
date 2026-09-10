async def insufficient_balance_handler(
    request: Request,
    exc: InsufficientBalanceError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )