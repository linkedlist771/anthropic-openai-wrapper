import json

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from litellm import acompletion

from anth2oai.configs import ConfigManager
from anth2oai.constants import (
    STREAMING_HEADERS,
)
import litellm
CODEX_RESPONSES_PREFIX = "openai/responses/"
litellm.drop_params = True


async def codex_streaming(api_key: str, body: dict):
    model_name = body.get("model", "").lower()
    messages = body.get("messages", [])
    tools = body.get("tools", [])
    if not model_name.startswith(CODEX_RESPONSES_PREFIX):
        model_name = CODEX_RESPONSES_PREFIX + model_name

    openai_base_url = await ConfigManager.get("OPENAI_BASE_URL")
    if not openai_base_url:
        raise HTTPException(
            f"OPENAI_BASE_URL is not set, set it in env or the database"
        )

    async def _stream_response():
        async for chunk in await acompletion(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            api_key=api_key,
            base_url=openai_base_url,
            # Literal["none", "minimal", "low", "medium", "high", "xhigh", "default"]
            # reasoning_effort="low",
            stream=True,
        ):
            yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _stream_response(),
        media_type="text/event-stream",
        headers=STREAMING_HEADERS,
    )
