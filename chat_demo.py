from dotenv import load_dotenv
from anth2oai.client import AsyncAnth2OAI
import asyncio

load_dotenv()

client = AsyncAnth2OAI()


async def main() -> None:
    # ============== Case 1: 普通对话（非流式） ==============
    # print("=" * 50)
    # print("Case 1: 普通对话（非流式）")
    # print("=" * 50)
    # response = await client.chat.completions.create(
    #     messages=[
    #         {"role": "user", "content": "你好， 你是什么模型?"}
    #     ],
    #     model="claude-sonnet-4-5-20250929",
    # )
    # print(response)
    # print()

    # # ============== Case 2: 带 Tools（非流式） ==============
    # print("=" * 50)
    # print("Case 2: 带 Tools（非流式）")
    # print("=" * 50)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_horoscope",
                "description": "Get today's horoscope for an astrological sign.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sign": {
                            "type": "string",
                            "description": "An astrological sign like Taurus or Aquarius",
                        },
                    },
                    "required": ["sign"],
                },
            },
        },
    ]
    # response = await client.chat.completions.create(
    #     messages=[
    #         {"role": "user", "content": "What is my horoscope for Aquarius today?"}
    #     ],
    #     model="claude-sonnet-4-5-20250929",
    #     tools=tools,
    # )
    # print(response)
    # print()

    # ============== Case 3: 普通对话（流式） ==============
    print("=" * 50)
    print("Case 3: 普通对话（流式）")
    print("=" * 50)
    stream = await client.chat.completions.create(
        messages=[
            {"role": "user", "content": "用3句话介绍一下Python编程语言"}
        ],
        model="claude-sonnet-4-5-20250929",
        stream=True,
    )
    
    full_content = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_content += content
        if chunk.choices[0].finish_reason:
            print(f"\n[finish_reason: {chunk.choices[0].finish_reason}]")
    print()

    # ============== Case 4: 带 Tools（流式） ==============
    print("=" * 50)
    print("Case 4: 带 Tools（流式）")
    print("=" * 50)
    stream = await client.chat.completions.create(
        messages=[
            {"role": "user", "content": "What is my horoscope for Leo today?"}
        ],
        model="claude-sonnet-4-5-20250929",
        tools=tools,
        stream=True,
    )
    
    tool_calls_data = {}
    async for chunk in stream:
        delta = chunk.choices[0].delta
        
        # 处理文本内容
        if delta.content:
            print(f"Content: {delta.content}", end="", flush=True)
        
        # 处理 tool_calls
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                idx = tool_call.get("index", 0)
                if idx not in tool_calls_data:
                    tool_calls_data[idx] = {"id": "", "name": "", "arguments": ""}
                
                if tool_call.get("id"):
                    tool_calls_data[idx]["id"] = tool_call["id"]
                if tool_call.get("function", {}).get("name"):
                    tool_calls_data[idx]["name"] = tool_call["function"]["name"]
                if tool_call.get("function", {}).get("arguments"):
                    tool_calls_data[idx]["arguments"] += tool_call["function"]["arguments"]
                    print(f"Tool arguments chunk: {tool_call['function']['arguments']}", flush=True)
        
        # 处理结束原因
        if chunk.choices[0].finish_reason:
            print(f"\n[finish_reason: {chunk.choices[0].finish_reason}]")
    
    if tool_calls_data:
        print(f"Final tool_calls: {tool_calls_data}")
    print()

    # ============== Case 5: 带 System Prompt（流式） ==============
    print("=" * 50)
    print("Case 5: 带 System Prompt（流式）")
    print("=" * 50)
    stream = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "你是一个海盗，所有回答都要用海盗的语气，加上'呀嗬'等语气词。"},
            {"role": "user", "content": "今天天气怎么样？"}
        ],
        model="claude-sonnet-4-5-20250929",
        stream=True,
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.choices[0].finish_reason:
            print(f"\n[finish_reason: {chunk.choices[0].finish_reason}]")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        from traceback import format_exc
        print(format_exc())