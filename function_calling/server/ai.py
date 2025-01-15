from typing import Any, cast
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionToolParam,
    ChatCompletionMessage,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
)
from openai.types.shared_params import FunctionDefinition
from server.schema import UserMessagePayload, AssistantMessagePayload
import json


def green_colour_attached_to_name(name: str) -> str:
    return f"{name}, you are now Green :)"


green_colour_attached_to_name_tool: ChatCompletionToolParam = ChatCompletionToolParam(
    type="function",
    function=FunctionDefinition(
        name="green_colour_attached_to_name",
        description="Use this to attach word 'Green' to the provided name.",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the person",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        strict=True,
    ),
)


client = OpenAI()

tools = [green_colour_attached_to_name_tool]


def handle_messages(
    messages: list[UserMessagePayload | AssistantMessagePayload],
) -> ChatCompletionMessage:
    transformed_messages = [
        ChatCompletionUserMessageParam(content=msg.content, role="user")
        if msg.role == "user"
        else ChatCompletionAssistantMessageParam(content=msg.content, role="assistant")
        for msg in messages
    ]
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            ChatCompletionSystemMessageParam(
                role="system",
                content="You are a helpful assistant. Before making a function call, make sure you know all the necessary information from the user.",
            ),
            *transformed_messages,
        ],
        tools=tools,
    )
    if completion.choices[0].finish_reason == "stop":
        return completion.choices[0].message
    elif completion.choices[0].finish_reason == "tool_calls":
        if completion.choices[0].message.tool_calls:
            tool_call: ChatCompletionMessageToolCall = completion.choices[
                0
            ].message.tool_calls[0]

            tool_call_id = tool_call.id

            function_name = tool_call.function.name
            arguments_dict = eval(tool_call.function.arguments)
            tool_call_result = getattr(globals()[function_name], "__call__")(
                **arguments_dict
            )
            tool_call_message = ChatCompletionAssistantMessageParam(
                role="assistant",
                tool_calls=[
                    ChatCompletionMessageToolCallParam(
                        **cast(ChatCompletionMessageToolCallParam, tool_call.to_dict())
                    )
                ],
            )

            function_call_result_message = ChatCompletionToolMessageParam(
                role="tool",
                content=json.dumps(
                    {"name": "Alex", "function_call_result": tool_call_result}
                ),
                tool_call_id=tool_call_id,
            )

            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content="You are a helpful assistant. Before making a function call, make sure you know all the necessary information from the user.",
                    ),
                    *transformed_messages,
                    tool_call_message,
                    function_call_result_message,
                ],
                tools=tools,
            )

            if completion.choices[0].finish_reason == "stop":
                return completion.choices[0].message

    return ChatCompletionMessage(role="assistant", content="Somethin went wrong")
