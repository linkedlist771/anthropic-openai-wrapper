<p align="center">
  <h1 align="center">🔄 anth2oai</h1>
  <p align="center">
    <strong>Anthropic Claude → OpenAI 格式代理服务</strong>
  </p>
  <p align="center">
    一键部署，让 Anthropic Claude 模型无缝兼容 OpenAI API 格式
  </p>
</p>

---

[![Python](https://img.shields.io/badge/python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13-blue?labelColor=grey&color=blue)](https://github.com/your-repo/anth2oai)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 项目简介

**anth2oai** 是一个轻量级代理服务，将 Anthropic Claude API 转换为 OpenAI 兼容格式。只需一键部署，即可在任何支持 OpenAI API 的工具中使用 Claude 模型。

### 🎯 适用场景

- **AI IDE 集成** - 在 Cursor、Continue、Windsurf 等 AI 编程助手中使用 Claude 模型
- **无缝切换** - 现有 OpenAI 代码无需修改，直接切换到 Claude
- **统一接口** - 用熟悉的 OpenAI 格式调用 Anthropic 模型

---

## 🚀 核心功能

- ✅ **完整 OpenAI 兼容** - 支持 `/v1/chat/completions` 标准接口
- ✅ **工具调用 (Tool Calling)** - 完美支持 Function Calling，适配 AI IDE
- ✅ **流式响应** - 支持 SSE 流式输出
- ✅ **同步/异步** - 同时提供 `Anth2OAI` 和 `AsyncAnth2OAI` 客户端
- ✅ **Web 管理面板** - 可视化配置 API Key 和代理设置
- ✅ **JWT 认证** - 安全的 API 访问控制

---

## 📦 快速开始

### 方式一：启动代理服务（推荐用于 AI IDE）
推荐使用docker部署，。 

服务启动后：
1. 访问 `http://localhost:8000/admin` 进入管理面板
2. 配置你的 Anthropic API Key
3. 设置访问密钥 (API_KEY)

### 方式二：作为 Python 客户端使用

```bash
pip install anth2oai
```

---

## 🔧 在 AI IDE 中配置

### Cursor 配置示例

在 Cursor 设置中配置自定义模型：

```
API Base URL: http://localhost:8000/v1
API Key: 你在管理面板设置的 API_KEY
Model: claude-sonnet-4-5-20250929
```

### 其他 AI IDE

任何支持自定义 OpenAI API 端点的工具都可以使用：
- **Continue** - 在 `~/.continue/config.json` 中配置
- **Windsurf** - 在设置中配置自定义模型
- **其他工具** - 设置 Base URL 为 `http://your-server:8000/v1`

---

## 📖 Python 客户端使用

### 异步客户端

```python
import asyncio
from anth2oai import AsyncAnth2OAI

async def main():
    client = AsyncAnth2OAI(
        api_key="your-anthropic-api-key",
        # base_url="https://api.anthropic.com"  # 可选：自定义端点
    )

    # 普通对话
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "你好，介绍一下自己"}
        ],
        model="claude-sonnet-4-5-20250929",
    )
    print(response.choices[0].message.content)

    # 流式输出
    stream = await client.chat.completions.create(
        messages=[{"role": "user", "content": "讲个笑话"}],
        model="claude-sonnet-4-5-20250929",
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

asyncio.run(main())
```

### 同步客户端

```python
from anth2oai import Anth2OAI

client = Anth2OAI(api_key="your-anthropic-api-key")

# 普通对话
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "你好！"}],
    model="claude-sonnet-4-5-20250929",
)
print(response.choices[0].message.content)

# 流式输出
for chunk in client.chat.completions.create(
    messages=[{"role": "user", "content": "从1数到5"}],
    model="claude-sonnet-4-5-20250929",
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## 🛠️ 工具调用 (Tool Calling)

完美支持 OpenAI 格式的工具调用，这是在 AI IDE 中实现代码编辑、文件操作等功能的关键：

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，如：北京、上海",
                    },
                },
                "required": ["location"],
            },
        },
    },
]

response = await client.chat.completions.create(
    messages=[{"role": "user", "content": "东京今天天气怎么样？"}],
    model="claude-sonnet-4-5-20250929",
    tools=tools,
)

# 处理工具调用
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        print(f"函数名: {tool_call.function.name}")
        print(f"参数: {tool_call.function.arguments}")
```

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ANTHROPIC_BASE_URL` | Anthropic API 端点 | `https://api.anthropic.com/v1` |
| `API_KEY` | 代理服务访问密钥 | - |

### Web 管理面板

访问 `/admin` 路径可进入管理面板：
- 设置代理服务访问密钥
- 配置 API 基础地址
- 修改管理员账号密码

默认账号密码：`admin` / `admin`（请在首次登录后修改）

---

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t anth2oai .

# 运行容器
docker run -d -p 8000:8000 \
  -e API_KEY=your-access-key \
  anth2oai
```

---


## 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

## 💡 致谢

本项目旨在简化 OpenAI 与 Anthropic API 之间的切换，让开发者能够更灵活地选择和使用不同的 LLM 服务。
