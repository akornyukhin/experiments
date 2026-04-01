from pydantic import BaseModel
from typing import List, Literal, Optional, Union, Iterable
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
    role: Literal["assistant"]
    content: Optional[str]


class MessagesPayload(BaseModel):
    messages: List[UserMessagePayload | AssistantMessagePayload]


class Person(BaseModel):
    name: str
    age: int
    gender: Literal["male", "female"]
