import json
from traceback import format_exc

import httpx
from anthropic._constants import DEFAULT_TIMEOUT
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from anth2oai.client import AsyncAnth2OAI
from anth2oai.configs import ConfigManager
from anth2oai.constants import (
    DEFAULT_HTTP_CLIENT_HEADERS,
    STREAMING_HEADERS,
)


async def claude_streaming(api_key: str, body: dict):
    anthropic_base_url = await ConfigManager.get(
        "ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"
    )
    http_client = httpx.AsyncClient(
        headers=DEFAULT_HTTP_CLIENT_HEADERS,
        base_url=anthropic_base_url,
        timeout=DEFAULT_TIMEOUT,
    )
    # DEFAULT_HTTP_CLIENT_HEADERS
    openai_client: AsyncAnth2OAI = AsyncAnth2OAI(
        api_key=api_key,
        base_url=anthropic_base_url,
        http_client=http_client,
    )
    streaming = await openai_client.chat.completions.create(**body)

    async def _stream_response():
        try:
            async for chunk in streaming:
                if hasattr(chunk, "model_dump"):
                    chunk_dict = chunk.model_dump()
                else:
                    chunk_dict = chunk
                yield f"data: {json.dumps(chunk_dict)}\n\n"

            yield "data: [DONE]\n\n"

        except HTTPException as e:
            error_chunk = {
                "error": {
                    "type": e.detail.get("type", "error")
                    if isinstance(e.detail, dict)
                    else "error",
                    "message": e.detail.get("message", str(e.detail))
                    if isinstance(e.detail, dict)
                    else str(e.detail),
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            logger.error(format_exc())
            error_chunk = {"error": {"type": "stream_error", "message": str(e)}}
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        _stream_response(),
        media_type="text/event-stream",
        headers=STREAMING_HEADERS,
    )
