from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, BaseModel, Field

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatCreate(BaseModel):
    chat_title: str = Field(default="New Chat", min_length=1, max_length=255)

class ChatResponse(BaseModel):
    id: int
    chat_title: str
    created_at: datetime = Field(
        validation_alias=AliasChoices("created_at", "chat_created_at"),
    )

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: MessageRole
    content: str
    created_at: datetime = Field(
        validation_alias=AliasChoices("created_at", "message_created_at"),
    )

    model_config = {"from_attributes": True}


class SendMessageResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
