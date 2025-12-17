from openai import OpenAI, AsyncOpenAI

from openai.resources.chat.chat import AsyncCompletions

from anthropic import omit
from typing_extensions import Literal, overload
from typing import AsyncIterator
import os
import asyncio
from anthropic import AsyncAnthropic
from loguru import logger
from .configs import DEFAULT_ANTHROPIC_BASE_URL, DEFAULT_MAX_TOKENS
from .format import (
    format_anthropic_response_to_openai_response,
    format_openai_tools_to_anthropic_tools,
    format_anthropic_stream_event_to_openai_chunk,
)
from anthropic.types.message import Message
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from typing import Any
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
    Function,
)
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage


class AsyncAnth2OAI(AsyncOpenAI):
    def __init__(self, *args, **kwargs) -> None:
        api_key = kwargs.get("api_key") or os.environ.get("OPENAI_API_KEY")
        base_url = kwargs.get("base_url") or os.environ.get("OPENAI_BASE_URL")
        # default anthropic base url
        assert api_key, "api_key is required"
        if not base_url:
            base_url = DEFAULT_ANTHROPIC_BASE_URL
            logger.warning(f"Base URL not provided, using default: {base_url}")
        # TODO: support other params.
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=base_url,
        )
        self.chat = type(
            "obj",
            (object,),
            {"completions": type("obj", (object,), {"create": self.create})()},
        )()

    @overload
    async def create(
        self,
        *,
        messages: list,
        model: str,
        stream: Literal[False] = False,
        tools: list | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> ChatCompletion: ...

    @overload
    async def create(
        self,
        *,
        messages: list,
        model: str,
        stream: Literal[True],
        tools: list | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> AsyncIterator[ChatCompletionChunk]: ...

    @overload
    async def create(
        self,
        *,
        messages: list,
        model: str,
        stream: bool,
        tools: list | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]: ...

    async def create(
        self,
        *,
        messages: list | None = None,
        model: str | None = None,
        stream: bool = False,
        tools: list | None = None,
        max_tokens: int | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]:
        """
        Create a chat completion, compatible with OpenAI API.
        """
        messages = messages or kwargs.get("messages")
        model = model or kwargs.get("model")

        # Convert tools
        anthropic_tools = format_openai_tools_to_anthropic_tools(tools)
        anthropic_tools = anthropic_tools or omit

        # Handle timeout and max_tokens
        # Note: timeout should stay None (not omit) as it's used by HTTP client
        max_tokens = max_tokens or DEFAULT_MAX_TOKENS

        # Extract system prompt
        system_prompt = omit
        messages = list(messages)  # Make a copy to avoid modifying original
        for i, message in enumerate(messages):
            if message.get("role") == "system":
                system_prompt = messages.pop(i).get("content", "")
                break

        if stream:
            return self._stream_create(
                messages=messages,
                model=model,
                system_prompt=system_prompt,
                tools=anthropic_tools,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        else:
            return await self._non_stream_create(
                messages=messages,
                model=model,
                system_prompt=system_prompt,
                tools=anthropic_tools,
                max_tokens=max_tokens,
                timeout=timeout,
            )

    async def _non_stream_create(
        self,
        messages: list,
        model: str,
        system_prompt,
        tools,
        max_tokens: int,
        timeout,
    ) -> ChatCompletion:
        """非流式请求"""
        anthropic_response = await self.client.messages.create(
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
            model=model,
            tools=tools,
            timeout=timeout,
        )
        return format_anthropic_response_to_openai_response(anthropic_response)

    async def _stream_create(
        self,
        messages: list,
        model: str,
        system_prompt,
        tools,
        max_tokens: int,
        timeout,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """流式请求"""
        async with self.client.messages.stream(
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
            model=model,
            tools=tools,
            timeout=timeout,
        ) as stream:
            async for event in stream:
                chunk = format_anthropic_stream_event_to_openai_chunk(event, model)
                if chunk:
                    yield chunk
