import os
import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv

from .services.llm import LLMService
from .graph import build_graph
from .chat import Chatbot
from .mcp.excalidraw_client import ExcalidrawClient

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


async def initialize_excalidraw(stack: AsyncExitStack, mcp_server_args):
    server_params = StdioServerParameters(
        command=mcp_server_args[0],
        args=[
            mcp_server_args[1],
            mcp_server_args[2]
        ],
    )

    read, write = await stack.enter_async_context(stdio_client(server_params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()

    tools = await load_mcp_tools(session)
    excalidraw = ExcalidrawClient(tools)

    read_me_tool = next(t for t in tools if t.name == "read_me")
    read_me_result = await read_me_tool.ainvoke({})

    return excalidraw, read_me_result


async def main():
    load_dotenv()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    llm = LLMService(api_key=os.getenv("GROQ_API_KEY"))
    command = os.getenv("EXCALIDRAW_MCP_COMMAND", "node")
    script_path = os.getenv("EXCALIDRAW_MCP_PATH")
    transport = os.getenv("EXCALIDRAW_MCP_TRANSPORT", "--stdio")

    mcp_args_list = [command, script_path, transport]

    async with AsyncExitStack() as stack:
        excalidraw, read_me = await initialize_excalidraw(stack, mcp_args_list)

        graph = build_graph(llm, excalidraw, redis_url=redis_url)
        bot = Chatbot(graph, read_me)

        await bot.chat()
    # stack closes stdio_client + ClientSession here, after chat ends


if __name__ == "__main__":
    asyncio.run(main())