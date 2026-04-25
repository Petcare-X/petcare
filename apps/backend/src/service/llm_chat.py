from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import LlmChat, LlmMessage
from src.schemas import MessageRole, ChatCreate, MessageCreate, MessageStatus, SendMessageResponse
from src.service.openrouter import OpenRouterService
from src.repositories import LlmChatRepository, LlmMessageRepository

class LLMChatService:
    def __init__(self):
        self.openrouter_service = OpenRouterService()
        self.chat_repo = LlmChatRepository()
        self.message_repo = LlmMessageRepository()

    def _build_openrouter_messages(
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

    async def create_chat(self, db: AsyncSession, user_id: int, payload: ChatCreate) -> LlmChat:
        chat = LlmChat(
            user_id=user_id, 
            chat_title=payload.chat_title,
            chat_custom_instructions=payload.chat_custom_instructions)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat
    
    async def get_user_chat(self, db: AsyncSession, user_id: int, chat_id: int) -> LlmChat:
        result = await self.get_user_chat(db, user_id, chat_id)
        return result

    async def get_user_chats(self, db: AsyncSession, user_id: int) -> list[LlmChat]:
        result = await self.chat_repo.get_by_user_id(db, user_id)
        return result

    async def get_chat_messages(self, db: AsyncSession, chat_id: int) -> list[LlmMessage]:
        result = await self.message_repo.get_by_chat_id(db, chat_id)
        return list(result.scalars().all())

    async def accept_message(self, db: AsyncSession, payload: MessageCreate) -> tuple[LlmMessage, LlmMessage]:
        chat = await self.get_user_chat(db, payload.user_id, payload.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found") #ChatNotFoundError
        
        if not payload.content:
            raise HTTPException(status_code=400, detail="Message content is required") #MessageContentRequiredError
        
        user_message = LlmMessage(
            chat_id=chat.id,
            user_id=chat.user_id,
            role=MessageRole.USER,
            content=payload.content,
            status=MessageStatus.COMPLETED
        )

        assistant_message = LlmMessage(
            chat_id=chat.id,
            user_id=chat.user_id,
            role=MessageRole.ASSISTANT,
            content="",
            parent_message_id=user_message.id,
            status=MessageStatus.PENDING
        )
        db.add(user_message)
        db.add(assistant_message)

        await db.commit()
        await db.refresh(user_message)
        await db.refresh(assistant_message)

        return SendMessageResponse(user_message, assistant_message)

# только pending 
    async def start_generation(self, db: AsyncSession, assistant_message_id: int, user_id: int) -> LlmMessage:
        assistant_message = await self.message_repo.get_by_id(db, assistant_message_id)
        if not assistant_message:
            raise HTTPException(status_code=404, detail="Assistant message not found") #AssistantMessageNotFoundError
        
        if assistant_message.user_id != user_id:
            raise HTTPException(status_code=403, detail="User does not have permission to access this message") #UserPermissionError
        
        if assistant_message.status != MessageStatus.PENDING:
            pass

        if assistant_message.role != MessageRole.ASSISTANT:
            raise HTTPException(status_code=400, detail="Assistant message is not valid") #AssistantMessageInvalidError

        assistant_message.status = MessageStatus.IN_PROGRESS
        assistant_message.error_message = None

        db.commit(assistant_message)
        await db.refresh(assistant_message)
        return assistant_message

    async def build_generation_context(self, db: AsyncSession, assistant_message_id: int) -> tuple[LlmChat, LlmMessage, list[LlmMessage], str]:
        assistant_message = await self.message_repo.get_by_id(db, assistant_message_id)
        if not assistant_message:
            raise HTTPException(status_code=404, detail="Assistant message not found") #AssistantMessageNotFoundError
        chat = await self.chat_repo.get_by_id(db, assistant_message.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found") #ChatNotFoundError
        user_message = await self.message_repo.get_by_id(db, assistant_message.parent_message_id)
        if not user_message:
            raise HTTPException(status_code=404, detail="User message not found") #UserMessageNotFoundError
        chat_history = await self.message_repo.get_by_chat_id(db, chat.id)
        if not chat_history:
            raise HTTPException(status_code=404, detail="Chat history not found") #ChatHistoryNotFoundError

        return (
            chat,
            assistant_message,
            chat_history,
            user_message.content
        )
    
    async def generate_answer(self, db: AsyncSession, assistant_message_id: int) -> LlmMessage:
        async with db.begin():
            assistant_message = self.start_generation(db, assistant_message_id)
            context = self.build_generation_context(db, assistant_message_id)
            
            try:
                assistant_text = await self.openrouter_service.generate_answer(
                    self._build_openrouter_messages(*context))
            except Exception as e:
                return {
                    "detail": str(e) # GenerationError
                }

# для бота
    async def send_message(self, db: AsyncSession, payload: MessageCreate) -> tuple[LlmMessage, LlmMessage]:
        chat = await self.get_user_chat(db, payload.user_id, payload.chat_id)
        history = await self.get_chat_messages(db, payload.user_id, payload.chat_id)

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
            self._build_openrouter_messages(chat, history, payload.content)
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