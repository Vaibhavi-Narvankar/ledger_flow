import socket

from fastapi import Request
from fastapi.responses import JSONResponse


async def database_failure_middleware(
    request: Request,
    call_next,
):
    try:
        return await call_next(request)

    except socket.gaierror:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database is currently unavailable",
            },
        )