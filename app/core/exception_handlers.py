from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import UserAlreadyExistsError


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