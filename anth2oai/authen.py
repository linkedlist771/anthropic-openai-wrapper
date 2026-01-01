from typing import Optional

from fastapi import Header, HTTPException, Request
from loguru import logger


async def validate_api_key(
    raw_request: Request,
    authorization: Optional[str] = Header(None),  # codex
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=f"Authorization is required in the header: authorization",
        )
    else:
        client_api_key = authorization.replace("Bearer ", "")
        return client_api_key
