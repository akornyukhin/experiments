from typing import Iterable, Literal, Union

from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartInputAudioParam,
    ChatCompletionContentPartTextParam,
)
from pydantic import BaseModel


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
