from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_db
from src.core.security import get_current_user

from src.schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse, SendMessageResponse
from src.service import LLMChatService
from src.models import UserInfo

chat_router = APIRouter(prefix="/llm-chat", tags=["llm-chat"])


@chat_router.post("/{pet_id}/create-chat", response_model=ChatResponse, status_code=200)
async def create_chat(
    payload: ChatCreate,
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
    service: LLMChatService = Depends(),
):
    return await service.create_chat(db=db, pet_id=pet_id, user_id=current_user.id, payload=payload)


@chat_router.get("/chats", response_model=list[ChatResponse])
async def get_user_chats(
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
    service: LLMChatService = Depends(),
):
    return await service.get_user_chats(db=db, user_id=current_user.id)

@chat_router.get("/chats/{pet_id}", response_model=list[ChatResponse])
async def get_pet_chats(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
    service: LLMChatService = Depends(),
):
    return await service.get_pet_user_chats(db=db, user_id=current_user.id, pet_id=pet_id)

@chat_router.post("/{pet_id}/{chat_id}/send-message", response_model=SendMessageResponse, status_code=202)
async def accept_message(
    chat_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
    service: LLMChatService = Depends(),
):
    user_message, assistant_message = await service.accept_message(db, current_user.id, chat_id, payload)
    generating_message = await service.start_generation(db, assistant_message.id, current_user.id)
    if generating_message:
        await service.generate_answer(generating_message.id)
    return SendMessageResponse(user_message=user_message, assistant_message=assistant_message)

@chat_router.get("/{pet_id}/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
    service: LLMChatService = Depends(),
):
    return await service.get_chat_messages(db=db, user_id=current_user.id, chat_id=chat_id)