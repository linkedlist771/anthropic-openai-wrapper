# from openai import


# from anthropic import Message


# Claude: ...
# NO tool:  Message(id='msg_01MpZ9gqYsiehLyRojvyiKw3', content=[TextBlock(citations=None, text='你好！我是 Claude，由 Anthropic 开发的 AI 助手。\n\n从我的系统提示来看，我目前运行在 Claude Code 环境中 - 这是 Anthropic 官方的 Claude 命令行界面（CLI）工具。\n\n我可以帮助你：\n- 编写和调试代码\n- 解答技术问题\n- 执行各种编程任务\n- 进行对话交流\n\n有什么我可以帮助你的吗？', type='text')], model='claude-sonnet-4-5-20250929', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=33, output_tokens=141, server_tool_use=None, service_tier='standard'))
# Tool:  Message(id='msg_01NtsGXNqy5yBCWLn1BA9WSG', content=[ToolUseBlock(id='toolu_01Mp8ZWdsBejbZ6cizeyyvqV', input={'location': 'San Francisco, CA'}, name='get_weather', type='tool_use')], model='claude-sonnet-4-5-20250929', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=601, output_tokens=56, server_tool_use=None, service_tier='standard'))

# Openai:
# No tool:
#         ChatCompletion(id='chatcmpl-6f78624fb108430db3d39130fe3ca5ea', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='\n\n我是通义千问，由通义实验室研发的超大规模语言模型。我可以帮助你回答问题、创作文字、编程、表达观点等。有什么我可以帮你的吗？', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[], reasoning_content='\n好的，用户问：“你好你是什么模型？”我需要先理解这个问题。用户可能是在询问我的身份，比如我是哪个公司的模型，或者我的功能是什么。根据提供的工具，我需要检查是否有相关的函数可以调用。\n\n看一下提供的工具列表，只有一个函数get_horoscope，用于获取今日星座运势。显然，这个函数和用户的问题无关。用户并没有询问星座相关的内容，而是想知道我的模型信息。因此，不需要调用任何工具函数。\n\n接下来，我应该直接回答用户的问题。需要明确说明我是通义千问，由通义实验室研发的大语言模型。同时，可以简要介绍我的功能，比如回答问题、创作文字、编程等，让用户了解我的能力。还要保持友好，邀请用户提问或给出任务，促进进一步的互动。\n\n需要确保回答简洁明了，不使用复杂术语，符合用户的语言习惯。同时，避免使用Markdown格式，保持自然的口语化表达。检查是否有遗漏的信息点，确保覆盖用户可能关心的部分，比如开发公司、模型名称、主要功能等。\n\n总结：用户的问题不涉及可用工具函数，直接回答身份和功能即可。\n'), stop_reason=None)], created=1765958701, model='Qwen3-235B-A22B', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=278, prompt_tokens=172, total_tokens=450, completion_tokens_details=None, prompt_tokens_details=None), prompt_logprobs=None, kv_transfer_params=None)
# {
#     "id": "chatcmpl-6f78624fb108430db3d39130fe3ca5ea",
#     "choices": [
#         {
#             "finish_reason": "stop",
#             "index": 0,
#             "logprobs": null,
#             "message": {
#                 "content": "\n\n\u6211\u662f\u901a\u4e49\u5343\u95ee\uff0c\u7531\u901a\u4e49\u5b9e\u9a8c\u5ba4\u7814\u53d1\u7684\u8d85\u5927\u89c4\u6a21\u8bed\u8a00\u6a21\u578b\u3002\u6211\u53ef\u4ee5\u5e2e\u52a9\u4f60\u56de\u7b54\u95ee\u9898\u3001\u521b\u4f5c\u6587\u5b57\u3001\u7f16\u7a0b\u3001\u8868\u8fbe\u89c2\u70b9\u7b49\u3002\u6709\u4ec0\u4e48\u6211\u53ef\u4ee5\u5e2e\u4f60\u7684\u5417\uff1f",
#                 "refusal": null,
#                 "role": "assistant",
#                 "annotations": null,
#                 "audio": null,
#                 "function_call": null,
#                 "tool_calls": [],
#                 "reasoning_content": "\n\u597d\u7684\uff0c\u7528\u6237\u95ee\uff1a\u201c\u4f60\u597d\u4f60\u662f\u4ec0\u4e48\u6a21\u578b\uff1f\u201d\u6211\u9700\u8981\u5148\u7406\u89e3\u8fd9\u4e2a\u95ee\u9898\u3002\u7528\u6237\u53ef\u80fd\u662f\u5728\u8be2\u95ee\u6211\u7684\u8eab\u4efd\uff0c\u6bd4\u5982\u6211\u662f\u54ea\u4e2a\u516c\u53f8\u7684\u6a21\u578b\uff0c\u6216\u8005\u6211\u7684\u529f\u80fd\u662f\u4ec0\u4e48\u3002\u6839\u636e\u63d0\u4f9b\u7684\u5de5\u5177\uff0c\u6211\u9700\u8981\u68c0\u67e5\u662f\u5426\u6709\u76f8\u5173\u7684\u51fd\u6570\u53ef\u4ee5\u8c03\u7528\u3002\n\n\u770b\u4e00\u4e0b\u63d0\u4f9b\u7684\u5de5\u5177\u5217\u8868\uff0c\u53ea\u6709\u4e00\u4e2a\u51fd\u6570get_horoscope\uff0c\u7528\u4e8e\u83b7\u53d6\u4eca\u65e5\u661f\u5ea7\u8fd0\u52bf\u3002\u663e\u7136\uff0c\u8fd9\u4e2a\u51fd\u6570\u548c\u7528\u6237\u7684\u95ee\u9898\u65e0\u5173\u3002\u7528\u6237\u5e76\u6ca1\u6709\u8be2\u95ee\u661f\u5ea7\u76f8\u5173\u7684\u5185\u5bb9\uff0c\u800c\u662f\u60f3\u77e5\u9053\u6211\u7684\u6a21\u578b\u4fe1\u606f\u3002\u56e0\u6b64\uff0c\u4e0d\u9700\u8981\u8c03\u7528\u4efb\u4f55\u5de5\u5177\u51fd\u6570\u3002\n\n\u63a5\u4e0b\u6765\uff0c\u6211\u5e94\u8be5\u76f4\u63a5\u56de\u7b54\u7528\u6237\u7684\u95ee\u9898\u3002\u9700\u8981\u660e\u786e\u8bf4\u660e\u6211\u662f\u901a\u4e49\u5343\u95ee\uff0c\u7531\u901a\u4e49\u5b9e\u9a8c\u5ba4\u7814\u53d1\u7684\u5927\u8bed\u8a00\u6a21\u578b\u3002\u540c\u65f6\uff0c\u53ef\u4ee5\u7b80\u8981\u4ecb\u7ecd\u6211\u7684\u529f\u80fd\uff0c\u6bd4\u5982\u56de\u7b54\u95ee\u9898\u3001\u521b\u4f5c\u6587\u5b57\u3001\u7f16\u7a0b\u7b49\uff0c\u8ba9\u7528\u6237\u4e86\u89e3\u6211\u7684\u80fd\u529b\u3002\u8fd8\u8981\u4fdd\u6301\u53cb\u597d\uff0c\u9080\u8bf7\u7528\u6237\u63d0\u95ee\u6216\u7ed9\u51fa\u4efb\u52a1\uff0c\u4fc3\u8fdb\u8fdb\u4e00\u6b65\u7684\u4e92\u52a8\u3002\n\n\u9700\u8981\u786e\u4fdd\u56de\u7b54\u7b80\u6d01\u660e\u4e86\uff0c\u4e0d\u4f7f\u7528\u590d\u6742\u672f\u8bed\uff0c\u7b26\u5408\u7528\u6237\u7684\u8bed\u8a00\u4e60\u60ef\u3002\u540c\u65f6\uff0c\u907f\u514d\u4f7f\u7528Markdown\u683c\u5f0f\uff0c\u4fdd\u6301\u81ea\u7136\u7684\u53e3\u8bed\u5316\u8868\u8fbe\u3002\u68c0\u67e5\u662f\u5426\u6709\u9057\u6f0f\u7684\u4fe1\u606f\u70b9\uff0c\u786e\u4fdd\u8986\u76d6\u7528\u6237\u53ef\u80fd\u5173\u5fc3\u7684\u90e8\u5206\uff0c\u6bd4\u5982\u5f00\u53d1\u516c\u53f8\u3001\u6a21\u578b\u540d\u79f0\u3001\u4e3b\u8981\u529f\u80fd\u7b49\u3002\n\n\u603b\u7ed3\uff1a\u7528\u6237\u7684\u95ee\u9898\u4e0d\u6d89\u53ca\u53ef\u7528\u5de5\u5177\u51fd\u6570\uff0c\u76f4\u63a5\u56de\u7b54\u8eab\u4efd\u548c\u529f\u80fd\u5373\u53ef\u3002\n"
#             },
#             "stop_reason": null
#         }
#     ],
#     "created": 1765958701,
#     "model": "Qwen3-235B-A22B",
#     "object": "chat.completion",
#     "service_tier": null,
#     "system_fingerprint": null,
#     "usage": {
#         "completion_tokens": 278,
#         "prompt_tokens": 172,
#         "total_tokens": 450,
#         "completion_tokens_details": null,
#         "prompt_tokens_details": null
#     },
#     "prompt_logprobs": null,
#     "kv_transfer_params": null
# }
# Tool:

#         ChatCompletion(id='chatcmpl-7bcf89f02afb40bd83901bdfe3c01f92', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content="\n\nThe tools available to me don't include a weather lookup function, so I can't provide the current weather in San Francisco. However, I can help with horoscope information if you'd like to share your astrological sign!", refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[], reasoning_content='\nOkay, the user is asking, "What is the weather in SF?" Let me see. The tools provided include a function called get_horoscope, which requires an astrological sign. But the user is asking about the weather in San Francisco. Hmm, the available tools don\'t have a weather-related function. The get_horoscope function isn\'t relevant here because it\'s about horoscopes, not weather. Since there\'s no function to fetch weather data, I should inform the user that I can\'t provide the weather information. I need to point out that none of the available tools can handle this request. So, the response should state that I can\'t assist with the weather in SF using the provided tools.\n'), stop_reason=None)], created=1765958646, model='Qwen3-235B-A22B', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=193, prompt_tokens=174, total_tokens=367, completion_tokens_details=None, prompt_tokens_details=None), prompt_logprobs=None, kv_transfer_params=None)
# {
#     "id": "chatcmpl-7bcf89f02afb40bd83901bdfe3c01f92",
#     "choices": [
#         {
#             "finish_reason": "stop",
#             "index": 0,
#             "logprobs": null,
#             "message": {
#                 "content": "\n\nThe tools available to me don't include a weather lookup function, so I can't provide the current weather in San Francisco. However, I can help with horoscope information if you'd like to share your astrological sign!",
#                 "refusal": null,
#                 "role": "assistant",
#                 "annotations": null,
#                 "audio": null,
#                 "function_call": null,
#                 "tool_calls": [],
#                 "reasoning_content": "\nOkay, the user is asking, \"What is the weather in SF?\" Let me see. The tools provided include a function called get_horoscope, which requires an astrological sign. But the user is asking about the weather in San Francisco. Hmm, the available tools don't have a weather-related function. The get_horoscope function isn't relevant here because it's about horoscopes, not weather. Since there's no function to fetch weather data, I should inform the user that I can't provide the weather information. I need to point out that none of the available tools can handle this request. So, the response should state that I can't assist with the weather in SF using the provided tools.\n"
#             },
#             "stop_reason": null
#         }
#     ],
#     "created": 1765958646,
#     "model": "Qwen3-235B-A22B",
#     "object": "chat.completion",
#     "service_tier": null,
#     "system_fingerprint": null,
#     "usage": {
#         "completion_tokens": 193,
#         "prompt_tokens": 174,
#         "total_tokens": 367,
#         "completion_tokens_details": null,
#         "prompt_tokens_details": null
#     },
#     "prompt_logprobs": null,
#     "kv_transfer_params": null
# }

from pydantic import BaseModel

from anthropic.types.message import Message
from openai.types.chat.chat_completion import (
    ChatCompletion,
    ChatCompletionMessage,
    Choice,
    CompletionUsage,
)
from typing import Any
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

import time
import json


from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice as ChunkChoice,
    ChoiceDelta,
)
import time


def format_anthropic_stream_event_to_openai_chunk(
    event,
    model: str,
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

    if event_type == "content_block_delta":
        delta = event.delta

        # Text delta
        if delta.type == "text_delta":
            return ChatCompletionChunk(
                id=f"chatcmpl-{int(time.time())}",
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=delta.text,
                            role=None,
                        ),
                        finish_reason=None,
                    )
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion.chunk",
            )

        # Tool use delta (input_json_delta)
        elif delta.type == "input_json_delta":
            # Tool arguments streaming
            return ChatCompletionChunk(
                id=f"chatcmpl-{int(time.time())}",
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=None,
                            tool_calls=[
                                {
                                    "index": 0,
                                    "function": {
                                        "arguments": delta.partial_json,
                                    },
                                }
                            ],
                        ),
                        finish_reason=None,
                    )
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion.chunk",
            )

    elif event_type == "content_block_start":
        content_block = event.content_block

        # Tool use start
        if content_block.type == "tool_use":
            return ChatCompletionChunk(
                id=f"chatcmpl-{int(time.time())}",
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(
                            content=None,
                            tool_calls=[
                                {
                                    "index": 0,
                                    "id": content_block.id,
                                    "type": "function",
                                    "function": {
                                        "name": content_block.name,
                                        "arguments": "",
                                    },
                                }
                            ],
                        ),
                        finish_reason=None,
                    )
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion.chunk",
            )

        # Text block start - send role
        elif content_block.type == "text":
            return ChatCompletionChunk(
                id=f"chatcmpl-{int(time.time())}",
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
                created=int(time.time()),
                model=model,
                object="chat.completion.chunk",
            )

    elif event_type == "message_delta":
        # Final message with stop reason
        stop_reason = getattr(event.delta, "stop_reason", None)
        if stop_reason:
            finish_reason = "tool_calls" if stop_reason == "tool_use" else "stop"
            return ChatCompletionChunk(
                id=f"chatcmpl-{int(time.time())}",
                choices=[
                    ChunkChoice(
                        index=0,
                        delta=ChoiceDelta(),
                        finish_reason=finish_reason,
                    )
                ],
                created=int(time.time()),
                model=model,
                object="chat.completion.chunk",
            )

    return None


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
