from collections.abc import AsyncIterator
from typing import Any

from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import StreamingResponse

from agents import Runner
from app.assistant import assistant
from app.mcp import lifespan
from app.store import MyChatKitStore


async def load_input_items(
    server: ChatKitServer,
    thread: ThreadMetadata,
    context: dict[str, Any],
):
    items_page = await server.store.load_thread_items(
        thread.id,
        after=None,
        limit=20,
        order="asc",
        context=context,
    )
    return await simple_to_agent_input(items_page.data)


def build_agent_context(
    thread: ThreadMetadata,
    server: ChatKitServer,
    context: dict[str, Any],
) -> AgentContext[dict[str, Any]]:
    return AgentContext(thread=thread, store=server.store, request_context=context)


class MyChatKitServer(ChatKitServer):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        input_items = await load_input_items(self, thread, context)
        agent_context = build_agent_context(thread, self, context)
        result = Runner.run_streamed(assistant, input_items, context=agent_context)
        async for event in stream_agent_response(agent_context, result):
            yield event


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    server = MyChatKitServer(store=MyChatKitStore())

    @app.post("/chatkit")
    async def chatkit(request: Request) -> Response:
        result = await server.process(await request.body(), context={})
        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        return Response(content=result.json, media_type="application/json")

    return app


app = create_app()
