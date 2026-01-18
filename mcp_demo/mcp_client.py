import asyncio
import os

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.context import RequestContext
from pydantic import AnyUrl


async def handle_sampling_message(
    context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    print(f"Sampling request: {params.messages}")
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stop_reason="endTurn",
    )

async def run():
    async with streamable_http_client(url="http://localhost:8000/mcp") as (read, write, get_session_id):
        async with ClientSession(read, write, sampling_callback=handle_sampling_message) as session:

            await session.initialize()  


            tools = await session.list_tools()

            for tool in tools:
                print(tool)

            a = 10
            b = "b"
            result = await session.call_tool(name="multiply", arguments={"a": a, "b": b})

            print(f"Multiplication result of {a} and {b} is {result}")
if __name__ == "__main__":
    asyncio.run(run())