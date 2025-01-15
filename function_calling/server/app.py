from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from server.schema import (
    RootResponse,
    AssistantMessagePayload,
    MessagesPayload,
)
from server.ai import handle_messages
from openai.types.chat import ChatCompletionMessage
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=RootResponse)
def get_root() -> RootResponse:
    return RootResponse(message="Hello World")


@app.post("/send_message", response_model=AssistantMessagePayload)
def send_message(payload: MessagesPayload) -> AssistantMessagePayload:
    # Simulate adding the message to the chat history
    result: ChatCompletionMessage = handle_messages(payload.messages)
    return AssistantMessagePayload(role="assistant", content=result.content)
