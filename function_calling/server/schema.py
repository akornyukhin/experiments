from pydantic import BaseModel
from typing import Literal, Union, Iterable
from openai.types.chat import (
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartInputAudioParam,
)


class RootResponse(BaseModel):
    message: str


class UserMessagePayload(BaseModel):
    role: Literal["user"]
    content: Union[
        str,
        Iterable[
            Union[
                ChatCompletionContentPartTextParam,
                ChatCompletionContentPartImageParam,
                ChatCompletionContentPartInputAudioParam,
            ]
        ],
    ]


class AssistantMessagePayload(BaseModel):
    content: str | None
    role: Literal["assistant"]


class MessagesPayload(BaseModel):
    messages: list[UserMessagePayload | AssistantMessagePayload]
