from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .agent_types import ToolDefinition


@dataclass
class McpServerConfig:
    """
    描述一个通过 stdio 启动的 MCP Server。

    MCP 支持多种 transport。这里只演示最简单的 stdio 模式。
    """

    name: str                          # MCP 服务器名称，用于生成工具前缀
    command: str                       # 启动 MCP Server 的命令，例如 python、npx 等
    args: list[str] = field(default_factory=list)  # 启动命令的参数列表
    env: dict[str, str] | None = None  # 可选的环境变量


def _extract_mcp_result_content(result: Any) -> dict[str, Any]:
    """
    把 MCP call_tool 的结果转换成普通 dict。

    demo6 的 ToolRegistry 约定工具返回 dict[str, Any]，
    但 MCP SDK 返回的是结构化对象，所以这里做一层格式适配。
    """
    content_items = getattr(result, "content", [])  # 安全取 result.content，不存在则返回空列表
    texts: list[str] = []

    for item in content_items:
        text = getattr(item, "text", None)  # 安全取 item.text，不存在则返回 None
        if text is not None:
            texts.append(text)              # 有 text 就收集
        else:
            texts.append(str(item))         # 没有 text 就转成字符串兜底

    return {
        "ok": not getattr(result, "isError", False),  # 没有 isError 就认为是成功
        "content": "\n".join(texts),                    # 把所有 text 拼成一段字符串
    }


async def _list_mcp_tools(server_config: McpServerConfig) -> list[Any]:
    """连接 MCP Server 并读取它暴露的工具列表。"""
    # 把 mcp_server_config 转成 stdio_client 需要的参数对象
    server_params = StdioServerParameters(
        command=server_config.command,
        args=server_config.args,
        env=server_config.env,
    )

    # async with 表示异步上下文管理器，进入时建立连接，退出时自动关闭
    async with stdio_client(server_params) as (read_stream, write_stream):
        # 在已建立的流上创建 MCP 客户端会话
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化会话，await 表示等待初始化完成
            await session.initialize()
            # 请求服务器列出所有可用工具，await 等待返回
            result = await session.list_tools()
            # 把结果转成普通 Python 列表返回
            return list(result.tools)


async def _call_mcp_tool(
    server_config: McpServerConfig,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """连接 MCP Server 并调用指定工具。"""
    server_params = StdioServerParameters(
        command=server_config.command,
        args=server_config.args,
        env=server_config.env,
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            # 调用指定工具，传入参数，await 等待执行结果
            result = await session.call_tool(tool_name, arguments)
            # 把 MCP 结果转成 demo6 框架能理解的 dict
            return _extract_mcp_result_content(result)


def load_mcp_tools(server_config: McpServerConfig) -> list[ToolDefinition]:
    """
    把一个 MCP Server 暴露的 tools 转换成 demo6 框架里的 ToolDefinition。

    - MCP Server 负责按标准协议暴露工具
    - demo6 Agent Runtime 仍然只认识 ToolDefinition
    - adapter 把两边接起来
    """
    # asyncio.run 启动一个新的事件循环，运行异步函数 _list_mcp_tools
    mcp_tools = asyncio.run(_list_mcp_tools(server_config))
    tool_definitions: list[ToolDefinition] = []

    for mcp_tool in mcp_tools:
        original_name = mcp_tool.name  # MCP Server 原始工具名
        exposed_name = f"{server_config.name}_{original_name}"  # demo6 里用的唯一工具名

        # 闭包 handler：把运行时传入的参数转发给真正的 MCP Server
        def handler(
            _tool_name: str = original_name,            # 通过默认参数闭包保存原始工具名
            _server_config: McpServerConfig = server_config,  # 通过默认参数闭包保存服务器配置
            **arguments: Any,                            # 运行时模型传进来的参数
        ) -> dict[str, Any]:
            # 同步代码里运行异步函数，调用真实 MCP 工具
            return asyncio.run(_call_mcp_tool(_server_config, _tool_name, arguments))

        # 把 MCP 工具包装成 demo6 的 ToolDefinition
        tool_definitions.append(
            ToolDefinition(
                name=exposed_name,
                description=f"[MCP:{server_config.name}] {mcp_tool.description or original_name}",
                parameters=mcp_tool.inputSchema,  # MCP 工具的参数 schema 直接复用
                handler=handler,
            )
        )

    return tool_definitions
