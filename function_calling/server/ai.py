import json
import os
from typing import Any, cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import FunctionDefinition

from server.logger import get_logger
from server.schema import AssistantMessagePayload, UserMessagePayload

logger = get_logger()


os.environ["OPENAI_API_KEY"] = "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"


def handle_tool_call(tool_call: ChatCompletionMessageToolCall) -> tuple[str, dict]:
    tool_call_id = tool_call.id
    function_name = tool_call.function.name
    arguments_dict = eval(tool_call.function.arguments)

    logger.info(f"Tool call ID: {tool_call_id}")
    logger.info(f"Function name: {function_name}")
    logger.info(f"Arguments dict: {arguments_dict}")

    result = getattr(globals()[function_name], "__call__")(**arguments_dict)

    logger.info(f"Result: {result}")

    result_dict = arguments_dict
    result_dict["function_call_result"] = result

    return tool_call_id, result_dict


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
    messages: list[UserMessagePayload | AssistantMessagePayload | ChatCompletionToolMessageParam | ChatCompletionAssistantMessageParam],
) -> ChatCompletionMessage:
    transformed_messages: list[ChatCompletionUserMessageParam |
                               ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam] = []
    for msg in messages:
        if isinstance(msg, UserMessagePayload):
            transformed_messages.append(
                ChatCompletionUserMessageParam(content=msg.content, role="user"))
        elif isinstance(msg, AssistantMessagePayload):
            transformed_messages.append(ChatCompletionAssistantMessageParam(
                content=msg.content, role="assistant"))
        else:
            transformed_messages.append(msg)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            ChatCompletionSystemMessageParam(
                role="system",
                content="You are a helpful assistant wtih access to a list of tools.",
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

            tool_call_id, tool_call_result_dict = handle_tool_call(tool_call)

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
                content=json.dumps(tool_call_result_dict),
                tool_call_id=tool_call_id,
            )

            logger.info(
                f"function_call_result_message: {function_call_result_message}")

            return handle_messages(
                messages=[
                    *messages,
                    tool_call_message,
                    function_call_result_message
                ]
            )

    return ChatCompletionMessage(role="assistant", content="Somethin went wrong")
