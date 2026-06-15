from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImageURL(BaseModel):
    url: str


class ChatContentPart(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: str
    text: str | None = None
    image_url: ImageURL | None = None


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    role: str
    content: list[ChatContentPart] = Field(min_length=1)


class ChatCompletionsRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    model: str
    messages: list[ChatMessage] = Field(min_length=1)
    stream: bool = False


class AssistantMessage(BaseModel):
    role: Literal["assistant"]
    content: str


class ChatCompletionChoice(BaseModel):
    index: int
    message: AssistantMessage
    finish_reason: Literal["stop"]


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: list[ChatCompletionChoice]
