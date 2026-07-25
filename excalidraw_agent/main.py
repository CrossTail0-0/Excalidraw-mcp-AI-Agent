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


async def initialize_excalidraw(stack: AsyncExitStack):
    server_params = StdioServerParameters(
        command="node",
        args=[
            r"C:/Users/oussa/Desktop/github/Excalidraw-mcp-AI-Agent/excalidraw-mcp/dist/index.js",
            "--stdio"
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

    llm = LLMService(api_key=os.getenv("GROQ_API_KEY"))

    async with AsyncExitStack() as stack:
        excalidraw, read_me = await initialize_excalidraw(stack)

        graph = build_graph(llm, excalidraw)
        bot = Chatbot(graph, read_me)

        await bot.chat()
    # stack closes stdio_client + ClientSession here, after chat ends


if __name__ == "__main__":
    asyncio.run(main())