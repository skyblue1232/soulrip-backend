from typing import Literal

from pydantic import Field

from app.schemas.common import CamelModel


class ChatMessage(CamelModel):
    role: str
    content: str


class ChatRequest(CamelModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = []
    language: Literal["ko", "en", "ja", "zh", "fr", "es", "de"] = "ko"


class ChatSource(CamelModel):
    type: str
    id: str
    title: str
    subtitle: str
    image_url: str = ""


class ChatResponse(CamelModel):
    answer: str
    sources: list[ChatSource]
    suggestions: list[str]
    used_ai: bool
