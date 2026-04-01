import os
from contextlib import asynccontextmanager

from agents.mcp import MCPServerStreamableHttp
from fastapi import FastAPI

from app.config import DEFAULT_STORE_MCP_URL


def create_store_mcp_server() -> MCPServerStreamableHttp:
    return MCPServerStreamableHttp(
        name="store-products",
        params={
            "url": os.getenv("STORE_MCP_URL", DEFAULT_STORE_MCP_URL),
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    )


store_mcp_server = create_store_mcp_server()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store_mcp_server.connect()
    try:
        yield
    finally:
        await store_mcp_server.cleanup()
