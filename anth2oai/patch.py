TOOL_PATCH_PREFIX = "op_"


def patch_payload_tools(tools: list[dict]) -> list[dict]:
    for tool in tools:
        name = tool.get("name")
        if name:
            name = f"{TOOL_PATCH_PREFIX}{name}"
            tool["name"] = name
    return tools
