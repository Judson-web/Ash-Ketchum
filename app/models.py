from typing import Literal, Optional
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str = Field(min_length=1, max_length=32000)


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    top_p: float = 0.9
    max_output_tokens: int = 2048
    messages: list[Message]


class ChatResponse(BaseModel):
    session_id: str
    model: str
    output_text: str


class HealthResponse(BaseModel):
    status: str
    firebase: str
    gemini: str
