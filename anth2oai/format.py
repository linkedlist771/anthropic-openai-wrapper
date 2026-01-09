# format.py

from anthropic.types.message import Message
from openai.types.chat.chat_completion import (
    ChatCompletion,
    ChatCompletionMessage,
    Choice,
    CompletionUsage,
)
from typing import Any, Optional
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from anthropic.types import Message, TextBlock, ToolUseBlock

import time
import json


from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice as ChunkChoice,
    ChoiceDelta,
    ChoiceDeltaToolCall,
    ChoiceDeltaToolCallFunction,
)
from .patch import TOOL_PATCH_PREFIX


class AnthropicStreamState:
    """Track state across streaming events for proper OpenAI format conversion."""

    def __init__(self):
        self.message_id: str = f"chatcmpl-{int(time.time())}"
        self.current_tool_index: int = -1
        self.sent_initial_role: bool = False
        self.current_content_block_index: int = -1
        self.current_content_block_type: Optional[str] = None


def format_anthropic_stream_event_to_openai_chunk(
    event,
    model: str,
    state: AnthropicStreamState,
) -> ChatCompletionChunk | None:
    """
    Convert Anthropic stream event to OpenAI ChatCompletionChunk format.

    Anthropic events:
    - message_start
    - content_block_start
    - content_block_delta (type: text_delta / input_json_delta)
    - content_block_stop
    - message_delta
    - message_stop
    """
    event_type = getattr(event, "type", None)
    created = int(time.time())

    if event_type == "message_start":
        # Send initial chunk with role
        state.sent_initial_role = True
        return ChatCompletionChunk(
            id=state.message_id,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=ChoiceDelta(
                        content="",
                        role="assistant",
                    ),
                    finish_reason=None,
                )
            ],
            created=created,
            model=model,
            object="chat.completion.chunk",
        )

    elif event_type == "content_block_start":
        content_block = event.content_block
        state.current_content_block_index = event.index
        state.current_content_block_type = content_block.type

        # Tool use start
        if content_block.type == "tool_use":
            state.current_tool_index += 1
            function_name = content_block.name
            function_name = function_name.replace(TOOL_PATCH_PREFIX, "")
            return ChatCompletionChunk(
                id=state.message_id,
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=None,
                            tool_calls=[
                                ChoiceDeltaToolCall(
                                    index=state.current_tool_index,
                                    id=content_block.id,
                                    type="function",
                                    function=ChoiceDeltaToolCallFunction(
                                        # name=content_block.name,
                                        name=function_name,
                                        arguments="",
                                    ),
                                )
                            ],
                        ),
                        finish_reason=None,
                    )
                ],
                created=created,
                model=model,
                object="chat.completion.chunk",
            )


        # Text block start - only send role if not already sent
        elif content_block.type == "text":
            if not state.sent_initial_role:
                state.sent_initial_role = True
                return ChatCompletionChunk(
                    id=state.message_id,
                    choices=[
                        ChunkChoice(
                            index=0,
                            delta=ChoiceDelta(
                                content="",
                                role="assistant",
                            ),
                            finish_reason=None,
                        )
                    ],
                    created=created,
                    model=model,
                    object="chat.completion.chunk",
                )
            # If role already sent, don't emit anything for text block start
            return None

    elif event_type == "content_block_delta":
        delta = event.delta

        # Text delta
        if delta.type == "text_delta":
            return ChatCompletionChunk(
                id=state.message_id,
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=delta.text,
                        ),
                        finish_reason=None,
                    )
                ],
                created=created,
                model=model,
                object="chat.completion.chunk",
            )

        # Tool use delta (input_json_delta)
        elif delta.type == "input_json_delta":
            return ChatCompletionChunk(
                id=state.message_id,
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=None,
                            tool_calls=[
                                ChoiceDeltaToolCall(
                                    index=state.current_tool_index,
                                    function=ChoiceDeltaToolCallFunction(
                                        arguments=delta.partial_json,
                                    ),
                                )
                            ],
                        ),
                        finish_reason=None,
                    )
                ],
                created=created,
                model=model,
                object="chat.completion.chunk",
            )

        # Thinking delta (if you want to support extended thinking)
        elif delta.type == "thinking_delta":
            # You can choose to emit this as content or skip it
            # Here we skip it, but you could convert to content if needed
            return None

    elif event_type == "content_block_stop":
        # Content block finished - usually no chunk needed
        state.current_content_block_type = None
        return None

    elif event_type == "message_delta":
        # Final message with stop reason
        stop_reason = getattr(event.delta, "stop_reason", None)
        if stop_reason:
            finish_reason = _anthropic_stop_to_openai_finish(stop_reason)
            return ChatCompletionChunk(
                id=state.message_id,
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(),
                        finish_reason=finish_reason,
                    )
                ],
                created=created,
                model=model,
                object="chat.completion.chunk",
            )

    elif event_type == "message_stop":
        # Stream is complete - no chunk needed
        return None

    return None


def _anthropic_stop_to_openai_finish(stop_reason: str) -> str:
    """Convert Anthropic stop_reason to OpenAI finish_reason."""
    mapping = {
        "end_turn": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls",
        "stop_sequence": "stop",
    }
    return mapping.get(stop_reason, "stop")


# ... rest of your existing functions remain the same ...


def format_openai_tools_to_anthropic_tools(openai_tools: list | None) -> list | None:
    """
    Convert OpenAI tools format to Anthropic tools format.

    OpenAI format:
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather",
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
    }

    Anthropic format:
    {
        "name": "get_weather",
        "description": "Get the weather",
        "input_schema": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
    """
    if not openai_tools:
        return None

    anthropic_tools = []

    for tool in openai_tools:
        # OpenAI tools have type "function" with nested function object
        if tool.get("type") == "function" and "function" in tool:
            func = tool["function"]
            anthropic_tool = {
                "name": func.get("name"),
                "description": func.get("description", ""),
                "input_schema": func.get(
                    "parameters",
                    {
                        "type": "object",
                        "properties": {},
                    },
                ),
            }
            anthropic_tools.append(anthropic_tool)
        else:
            # If it's already in a simple format, try to convert directly
            anthropic_tool = {
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "input_schema": tool.get("parameters")
                or tool.get(
                    "input_schema",
                    {
                        "type": "object",
                        "properties": {},
                    },
                ),
            }
            anthropic_tools.append(anthropic_tool)

    return anthropic_tools if anthropic_tools else None


def format_anthropic_response_to_openai_response(
    anthropic_response: Message,
) -> ChatCompletion:
    """
    Convert Anthropic Message response to OpenAI ChatCompletion format.
    Handles both tool calls and regular text responses.
    """
    # Build message content and tool calls
    content, tool_calls = _build_message_content(anthropic_response.content)

    # Determine finish reason
    finish_reason = _get_finish_reason(anthropic_response.stop_reason)

    # Build the message
    message = ChatCompletionMessage(
        content=content,
        role="assistant",
        refusal=None,
        annotations=None,
        audio=None,
        function_call=None,
        tool_calls=tool_calls if tool_calls else None,
    )

    # Build choice
    choice = Choice(
        finish_reason=finish_reason,
        index=0,
        logprobs=None,
        message=message,
    )

    # Build usage
    usage = _build_usage(anthropic_response.usage)

    return ChatCompletion(
        id=_convert_id(anthropic_response.id),
        choices=[choice],
        created=int(time.time()),
        model=anthropic_response.model,
        object="chat.completion",
        service_tier=None,
        system_fingerprint=None,
        usage=usage,
    )


def _build_message_content(
    content_blocks: list,
) -> tuple[str | None, list[ChatCompletionMessageToolCall] | None]:
    """
    Build message content and tool calls from Anthropic content blocks.
    Returns (text_content, tool_calls)
    """
    text_parts = []
    tool_calls = []

    for block in content_blocks:
        if isinstance(block, TextBlock) or (
            hasattr(block, "type") and block.type == "text"
        ):
            text_parts.append(block.text)
        elif isinstance(block, ToolUseBlock) or (
            hasattr(block, "type") and block.type == "tool_use"
        ):
            tool_call = ChatCompletionMessageToolCall(
                id=block.id,
                type="function",
                function=Function(
                    name=block.name,
                    arguments=json.dumps(block.input)
                    if isinstance(block.input, dict)
                    else str(block.input),
                ),
            )
            tool_calls.append(tool_call)

    text_content = "\n".join(text_parts) if text_parts else None

    return text_content, tool_calls if tool_calls else None


def _get_finish_reason(stop_reason: str | None) -> str:
    """Convert Anthropic stop_reason to OpenAI finish_reason."""
    mapping = {
        "end_turn": "stop",
        "max_tokens": "length",
        "tool_use": "tool_calls",
        "stop_sequence": "stop",
    }
    return mapping.get(stop_reason, "stop")


def _build_usage(anthropic_usage: Any) -> CompletionUsage:
    """Build OpenAI CompletionUsage from Anthropic Usage."""
    input_tokens = getattr(anthropic_usage, "input_tokens", 0) if anthropic_usage else 0
    output_tokens = (
        getattr(anthropic_usage, "output_tokens", 0) if anthropic_usage else 0
    )

    return CompletionUsage(
        completion_tokens=output_tokens,
        prompt_tokens=input_tokens,
        total_tokens=input_tokens + output_tokens,
        completion_tokens_details=None,
        prompt_tokens_details=None,
    )


def _convert_id(anthropic_id: str) -> str:
    """Convert Anthropic ID format to OpenAI ID format."""
    # Replace 'msg_' prefix with 'chatcmpl-' to match OpenAI format
    if anthropic_id.startswith("msg_"):
        return "chatcmpl-" + anthropic_id[4:]
    return "chatcmpl-" + anthropic_id
