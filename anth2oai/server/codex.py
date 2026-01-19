import json

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from litellm import acompletion
from loguru import logger

from anth2oai.configs import ConfigManager
from anth2oai.constants import (
    STREAMING_HEADERS,
)

CODEX_RESPONSES_PREFIX = "openai/responses/"
# import litellm

# litellm.drop_params = True
# litellm.verbose = True


def format_responses_tools_to_chat_completion(tools: list[dict]) -> list[dict]:
    converted_tools = []

    for tool in tools:
        tool_type = tool.get("type")
        if tool_type == "function" and "function" in tool:
            converted_tools.append(tool)
            continue
        if tool_type in ("function", "custom"):
            converted_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.get("name"),
                        "description": tool.get("description"),
                        "parameters": tool.get(
                            "parameters", {"type": "object", "properties": {}}
                        ),
                        **({"strict": tool["strict"]} if "strict" in tool else {}),
                    },
                }
            )
        else:
            converted_tools.append(tool)

    return converted_tools


async def codex_streaming(api_key: str, body: dict):
    model_name = body.get("model", "").lower()
    messages = body.get("messages", [])
    tools = body.get("tools", [])
    tools = format_responses_tools_to_chat_completion(tools)
    if not model_name.startswith(CODEX_RESPONSES_PREFIX):
        model_name = CODEX_RESPONSES_PREFIX + model_name

    openai_base_url = await ConfigManager.get("OPENAI_BASE_URL")
    if not openai_base_url:
        raise HTTPException(
            f"OPENAI_BASE_URL is not set, set it in env or the database"
        )

    # params = {
    #     "model": model_name,
    #     "messages": messages,
    #     "tools": tools,
    #     "tool_choice": "auto",
    #     "api_key": api_key,
    #     "base_url": openai_base_url,
    #     "stream": True,
    # }
    # from loguru import logger
    # import json
    # from pathlib import Path

    # saving_path = Path("/workspace/debug.json")
    # logger.debug(json.dumps(params, indent=4))
    # with saving_path.open("w") as f:
    #     f.write(json.dumps(params, indent=4) + "\n")

    async def _stream_response():
        # 调试日志：打印所有关键参数（使用 info 级别确保能看到）
        logger.info(f"=== codex_streaming 调试信息 ===")
        logger.info(f"model_name: {model_name}")
        logger.info(f"api_key: {api_key[:10] if api_key else 'None'}...")  # 只显示前10位
        logger.info(f"api_key is None: {api_key is None}")
        logger.info(f"api_key type: {type(api_key)}")
        logger.info(f"openai_base_url: {openai_base_url}")
        logger.info(f"openai_base_url is None: {openai_base_url is None}")
        logger.info(f"messages count: {len(messages) if messages else 'None'}")
        logger.info(f"tools count: {len(tools) if tools else 'None'}")
        logger.info(f"================================")
        
        try:
            async for chunk in await acompletion(
                model=model_name,
                messages=messages,
                tools=tools,
                # tool_choice="auto",
                api_key=api_key,
                base_url=openai_base_url,
                # Literal["none", "minimal", "low", "medium", "high", "xhigh", "default"]
                # reasoning_effort="low",
                stream=True,
            ):
                yield f"data: {json.dumps(chunk.model_dump())}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"=== acompletion 调用失败 ===")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"参数检查:")
            logger.error(f"  - api_key 是否为空: {not api_key}")
            logger.error(f"  - base_url 是否为空: {not openai_base_url}")
            logger.error(f"  - model: {model_name}")
            import traceback
            logger.error(f"完整堆栈: {traceback.format_exc()}")
            raise

    return StreamingResponse(
        _stream_response(),
        media_type="text/event-stream",
        headers=STREAMING_HEADERS,
    )
