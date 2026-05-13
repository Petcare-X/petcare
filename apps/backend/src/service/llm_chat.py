from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import AsyncSessionLocal
from src.models import LlmChat, LlmMessage
from src.schemas import MessageRole, ChatCreate, MessageCreate, MessageStatus, SendMessageRequest, SendMessageResponse
from src.service.openrouter import OpenRouterService
from src.repositories import LlmChatRepository, LlmMessageRepository, PetsRepository
from src.exceptions import (ChatNotFound, 
                            UserMessageError, 
                            AssistantMessageNotFound, 
                            AssistantMessageError, 
                            ChatHistoryNotFound, 
                            UserMessageError,
                            UserMessageNotFound, 
                            UserPermissionError,
                            MessageGenerationError,
                            PetNotFoundError)

class LLMChatService:
    def __init__(self):
        self.openrouter_service = OpenRouterService()
        self.chat_repo = LlmChatRepository()
        self.message_repo = LlmMessageRepository()
        self.pet_repo = PetsRepository()
        self.session_factory = AsyncSessionLocal

    def build_openrouter_messages(
        self,
        chat: LlmChat,
        history: list[LlmMessage],
        current_content: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if chat.chat_custom_instructions:
            messages.append(
                {
                    "role": MessageRole.SYSTEM.value,
                    "content": chat.chat_custom_instructions,
                }
            )

        for message in history:
            messages.append(
                {
                    "role": str(message.role),
                    "content": message.content,
                }
            )

        messages.append(
            {
                "role": MessageRole.USER.value,
                "content": current_content,
            }
        )
        return messages
    
    async def failed_message(self, db: AsyncSession, message_id: int, error_message: str) -> LlmMessage:
        assistant_message = await self.message_repo.get_by_id(db, message_id)
        assistant_message.status = MessageStatus.FAILED
        assistant_message.error_message = error_message
        await db.commit()
        await db.refresh(assistant_message)
        return assistant_message

    async def create_chat(self, db: AsyncSession, pet_id: int, user_id: int, payload: ChatCreate) -> LlmChat:
        pet = await self.pet_repo.get_by_id(db, pet_id)
        if not pet:
            raise PetNotFoundError()
        chat = LlmChat(
            user_id=user_id, 
            pet_id=pet_id,
            chat_title=payload.chat_title,
            chat_custom_instructions=payload.chat_custom_instructions)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat
    
    async def get_user_chat(self, db: AsyncSession, user_id: int, chat_id: int) -> LlmChat:
        result = await self.chat_repo.get_user_chat(db, user_id, chat_id)
        if not result:
            raise ChatNotFound("Chat not found")
        return result

    async def get_user_chats(self, db: AsyncSession, user_id: int) -> list[LlmChat]:
        result = await self.chat_repo.get_by_user_id(db, user_id)
        if not result:
            raise ChatNotFound("Chats not found")
        return result

    async def get_pet_user_chats(self, db: AsyncSession, user_id: int, pet_id: int) -> list[LlmChat]:
        pet = await self.pet_repo.get_by_id(db, pet_id)
        if not pet:
            raise PetNotFoundError()
        result = await self.chat_repo.get_by_user_pet(db, user_id=user_id, pet_id=pet_id)
        if not result:
            raise ChatNotFound("Chats not found")
        return result

    async def get_chat_messages(self, db: AsyncSession, user_id: int, pet_id: int, chat_id: int) -> list[LlmMessage]:
        chat = await self.chat_repo.get_user_chat(db, user_id, chat_id)
        if not chat:
            raise UserPermissionError("User does not have permission to access this chat")
        if chat.pet_id != pet_id:
            raise UserPermissionError("User does not have permission to access this chat")
        messages = await self.message_repo.get_by_chat_id(db, chat_id)
        return messages

    async def accept_message(
        self,
        db: AsyncSession,
        user_id: int,
        pet_id: int,
        chat_id: int,
        payload: SendMessageRequest,
    ) -> tuple[LlmMessage, LlmMessage]:
        chat = await self.get_user_chat(db, user_id, chat_id)
        if not chat:
            raise ChatNotFound("Chat not found")
        if chat.pet_id != pet_id:
            raise UserPermissionError("User does not have permission to access this chat")
        
        if not payload.content:
            raise UserMessageError("Message content is required")
        
        user_message = LlmMessage(
            chat_id=chat_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=payload.content,
            status=MessageStatus.COMPLETED
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)

        assistant_message = LlmMessage(
            chat_id=chat_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content="",
            parent_message_id=user_message.id,
            status=MessageStatus.PENDING
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)

        return (user_message, assistant_message)

    async def start_generation(self, db: AsyncSession, assistant_message_id: int, user_id: int) -> LlmMessage | None:
        assistant_message = await self.message_repo.get_by_id(db, assistant_message_id)
        if not assistant_message:
            raise AssistantMessageNotFound("Assistant message not found")
        
        if assistant_message.user_id != user_id:
            raise UserPermissionError("User does not have permission to access this message")
        
        if assistant_message.role != MessageRole.ASSISTANT:
            raise AssistantMessageError("Assistant message is not valid")
        
        if assistant_message.status == MessageStatus.FAILED:
            pass
        else:
            assistant_message.status = MessageStatus.IN_PROGRESS
            assistant_message.error_message = None

            await db.commit()
            await db.refresh(assistant_message)
            return assistant_message

    async def build_generation_context(self, db: AsyncSession, assistant_message_id: int) -> tuple[LlmChat, list[LlmMessage], str]:
        assistant_message = await self.message_repo.get_by_id(db, assistant_message_id)
        if not assistant_message:
            raise AssistantMessageNotFound("Assistant message not found")
        
        chat = await self.chat_repo.get_by_id(db, assistant_message.chat_id)
        if not chat:
            assistant_message = await self.failed_message(db, assistant_message.id, "Chat not found")
            raise ChatNotFound("Chat not found")
        
        user_message = await self.message_repo.get_by_id(db, assistant_message.parent_message_id)
        if not user_message:
            assistant_message = await self.failed_message(db, assistant_message.id, "User message not found")
            raise UserMessageNotFound("User message not found")
        if user_message.role != MessageRole.USER:
            assistant_message = await self.failed_message(db, assistant_message.id, "User message is not valid")
            raise UserMessageError("User message is not valid")
        
        chat_history = await self.message_repo.get_by_chat_id(db, chat.id)
        if not chat_history:
            assistant_message = await self.failed_message(db, assistant_message.id, "Chat history not found")
            raise ChatHistoryNotFound("Chat history not found")
        if chat_history[-1].role == MessageRole.ASSISTANT:
            chat_history = chat_history[:-1]

        return (chat,
                chat_history,
                user_message.content)
    
    async def generate_answer(self, assistant_message_id: int) -> LlmMessage:
        async with self.session_factory() as db:
            assistant_message = await self.message_repo.get_by_id(db, assistant_message_id)
            context = await self.build_generation_context(db, assistant_message_id)
            try:
                assistant_text = await self.openrouter_service.generate_answer(
                    self.build_openrouter_messages(*context))
                if assistant_text:
                    assistant_message.content = assistant_text
                    assistant_message.status = MessageStatus.COMPLETED
                    assistant_message.error_message = None

                    await db.commit()
                    await db.refresh(assistant_message)
                    return assistant_message

            except Exception as e:
                error_message = f"Error generating answer: {str(e)}"
                assistant_message = await self.failed_message(db, assistant_message_id, error_message)
                raise MessageGenerationError(error_message)

# для бота
    async def send_message(self, db: AsyncSession, user_id: int, payload: MessageCreate) -> tuple[LlmMessage, LlmMessage]:
        chat = await self.get_user_chat(db, user_id, payload.chat_id)
        if not chat:
            raise ChatNotFound("Chat not found")
        chat_history = await self.message_repo.get_by_chat_id(db, payload.chat_id)
        if not chat_history:
            raise ChatHistoryNotFound("Chat history not found")
        user_message = LlmMessage(
            chat_id=chat.id,
            user_id=chat.user_id,
            role=MessageRole.USER,
            status=MessageStatus.COMPLETED,
            content=payload.content,
        )
        db.add(user_message)
        await db.flush()

        assistant_text = await self.openrouter_service.generate_answer(
            self.build_openrouter_messages(chat, chat_history, payload.content)
        )

        assistant_message = LlmMessage(
            chat_id=chat.id,
            user_id=chat.user_id,
            role=MessageRole.ASSISTANT,
            status=MessageStatus.COMPLETED,
            parent_message_id=user_message.id,
            content=assistant_text,
        )
        db.add(assistant_message)

        await db.commit()
        await db.refresh(user_message)
        await db.refresh(assistant_message)

        return user_message, assistant_message
    
    async def delete_chat(self, db: AsyncSession, user_id: int, pet_id: int, chat_id: int) -> None:
        chat = await self.get_user_chat(db, user_id, chat_id)
        if chat.pet_id != pet_id:
            raise UserPermissionError("User does not have permission to access this chat")
        await self.chat_repo.delete(db, chat)
