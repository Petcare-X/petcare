from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, BaseModel, Field

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ChatCreate(BaseModel):
    chat_title: str = Field(default="New Chat", min_length=1, max_length=255)
    chat_custom_instructions: str | None = Field(default=None, min_length=0, max_length=5000)

class ChatResponse(BaseModel):
    id: int
    pet_id: int
    chat_title: str
    created_at: datetime = Field(
        validation_alias=AliasChoices("created_at", "chat_created_at"),
    )

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    chat_id: int
    content: str = Field(..., min_length=1, max_length=5000)


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int
    role: MessageRole
    content: str
    parent_message_id: int | None
    status: MessageStatus
    error_message: str | None
    created_at: datetime = Field(
        validation_alias=AliasChoices("created_at", "message_created_at"),
    )

    model_config = {"from_attributes": True}

class SendMessages(BaseModel):
    content: str

class SendMessageResponse(BaseModel):
    user_message: MessageResponse | None
    assistant_message: MessageResponse | None
