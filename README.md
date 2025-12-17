<p align="center">
  <h1 align="center">🔄 anth2oai</h1>
  <p align="center">
    <strong>Anthropic to OpenAI API Wrapper</strong>
  </p>
  <p align="center">
    Use Anthropic's Claude models with OpenAI-compatible API interface
  </p>
</p>

---

[![Python](https://img.shields.io/badge/python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13-blue?labelColor=grey&color=blue)](https://github.com/your-repo/anth2oai)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

**anth2oai** is a lightweight wrapper that allows you to use Anthropic's Claude models through an OpenAI-compatible API interface. This makes it easy to switch between OpenAI and Anthropic models in your existing codebase with minimal changes. Currently, we support the `chat.completion` interface for both Sync and ASync method, with tool call support.

### Features

- ✅ **OpenAI-compatible interface** - Drop-in replacement for OpenAI client
- ✅ **Async & Sync support** - Both `AsyncAnth2OAI` and `Anth2OAI` clients available
- ✅ **Streaming support** - Full support for streaming responses
- ✅ **Tool/Function calling** - Automatic conversion of OpenAI tools format to Anthropic format
- ✅ **System prompts** - Automatic handling of system messages
- ✅ **Custom base URL** - Support for Anthropic API proxies

---

## Installation

```bash
pip install anth2oai
```

Or install from source:

```bash
git clone https://github.com/your-repo/anth2oai.git
cd anth2oai
pip install -e .
```

---

## Quick Start

### Async Client

```python
import asyncio
from anth2oai import AsyncAnth2OAI

async def main():
    client = AsyncAnth2OAI(
        api_key="your-anthropic-api-key",
        # base_url="https://api.anthropic.com"  # Optional: custom endpoint
    )

    # Non-streaming
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, who are you?"}
        ],
        model="claude-sonnet-4-5-20250929",
    )
    print(response.choices[0].message.content)

    # Streaming
    stream = await client.chat.completions.create(
        messages=[{"role": "user", "content": "Tell me a joke"}],
        model="claude-sonnet-4-5-20250929",
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

asyncio.run(main())
```

### Sync Client

```python
from anth2oai import Anth2OAI

client = Anth2OAI(
    api_key="your-anthropic-api-key",
)

# Non-streaming
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello!"}],
    model="claude-sonnet-4-5-20250929",
)
print(response.choices[0].message.content)

# Streaming
for chunk in client.chat.completions.create(
    messages=[{"role": "user", "content": "Count to 5"}],
    model="claude-sonnet-4-5-20250929",
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## Tool/Function Calling

The wrapper automatically converts OpenAI's tool format to Anthropic's format:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., San Francisco",
                    },
                },
                "required": ["location"],
            },
        },
    },
]

response = await client.chat.completions.create(
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    model="claude-sonnet-4-5-20250929",
    tools=tools,
)

# Check for tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"Function: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

---

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
export OPENAI_API_KEY="your-anthropic-api-key"
export OPENAI_BASE_URL="https://api.anthropic.com"  # Optional
```

Then simply:

```python
client = AsyncAnth2OAI()  # Will use env variables
```

### Available Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api_key` | Anthropic API key | `OPENAI_API_KEY` env var |
| `base_url` | API endpoint URL | `https://api.anthropic.com` |
| `max_tokens` | Maximum tokens in response | `1024` |
| `timeout` | Request timeout in seconds | `None` |

---

### TODO:

- [x] Support Sync and Async interface for `chat.completion`.
- [ ] Support MultiModal Input.
- [ ] Suppor the `response` interface.


---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

This project is inspired by the need to easily switch between OpenAI and Anthropic APIs in production applications.
