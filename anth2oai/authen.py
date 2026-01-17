from typing import Optional

from fastapi import Header, HTTPException, Request
from loguru import logger

from anth2oai.configs import ConfigManager


async def validate_api_key(
    raw_request: Request,
    authorization: Optional[str] = Header(None),  # codex
):
    """
    Validate API key from Authorization header.
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization is required in the header",
        )

    client_api_key = authorization.replace("Bearer ", "")
    return client_api_key
