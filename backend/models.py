"""Pydantic models: what the API accepts and returns."""
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class SessionCreated(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4000)
    model: str | None = Field(default=None, min_length=1, max_length=100)


class ChatResponse(BaseModel):
    reply: str
    input_tokens: int
    output_tokens: int
    seconds: float
    cost: float | None
    turns_in_memory: int
    guardrail: str | None = None


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SessionHistory(BaseModel):
    session_id: str
    messages: list[Message]


class DeleteResponse(BaseModel):
    deleted: bool


class ModelOption(BaseModel):
    id: str
    label: str


class ModelGroup(BaseModel):
    provider: str
    models: list[ModelOption]


class ModelList(BaseModel):
    default: str
    providers: list[ModelGroup]


class GuardrailConfig(BaseModel):
    enabled: bool
    max_input_chars: int = Field(..., gt=0)
    block_injection: bool
    injection_phrases: list[str]
    mask_pii: bool
    topic_check: bool
    allowed_topic: str = Field(..., min_length=1)
    max_output_words: int = Field(..., gt=0)
    banned_output_words: list[str]
    blocked_message: str = Field(..., min_length=1)
