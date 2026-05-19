import asyncio
import httpx
from dataclasses import dataclass
from asyncio import Semaphore

from src.core.config import settings
from src.exceptions import (OpenRouterApiError,
                            OpenRouterResponseError)
from src.core.prompt_loader import load_system_prompt
from src.models import LlmChat, LlmMessage
from src.schemas import MessageRole

@dataclass(slots=True)
class GenerationSettings:
    model: str
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.8
    timeout_seconds: float = 60.0
    max_history_length: int = 12
    max_request_attempts: int = 3
    retry_delay_seconds: float = 1.0

class OpenRouterService:
    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.generation_settings = GenerationSettings(
            model=settings.OPENROUTER_MODEL)
        self._semaphore = Semaphore(3)

    async def generate_answer(self, messages: list[dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.generation_settings.model,
            "messages": messages,
            "temperature": self.generation_settings.temperature,
            "max_tokens": self.generation_settings.max_tokens,
            "top_p": self.generation_settings.top_p,
        }

        timeout = httpx.Timeout(self.generation_settings.timeout_seconds)

        async with self._semaphore:
            last_error: httpx.RequestError | None = None
            for attempt in range(1, self.generation_settings.max_request_attempts + 1):
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(self.base_url, headers=headers, json=payload)
                    break
                except httpx.RequestError as exc:
                    last_error = exc
                    if attempt == self.generation_settings.max_request_attempts:
                        raise OpenRouterApiError(
                            f"OpenRouter network error: {exc}"
                        ) from exc
                    await asyncio.sleep(self.generation_settings.retry_delay_seconds)

        if response.status_code >= 400:
            raise OpenRouterApiError(f"OpenRouter API error: {response.text}")

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise OpenRouterResponseError("Invalid response from OpenRouter")
        
    def build_system_prompt(self, chat: LlmChat) -> str:
        base_prompt = load_system_prompt()
        custom_instructions = chat.chat_custom_instructions or ""

        if not custom_instructions:
            return base_prompt
        
        return (
            f"{base_prompt}\n\n" \
            "## Инструкции от пользователя на этот чат \n\n" \
            "Используй их, если они не противоречат основным инструкциям" \
            f"{custom_instructions}")
    
    def trim_history(self, history: list[LlmMessage], current_content) -> list[dict[str, str]]:
        filtered_history = [msg for msg in history if msg.role != MessageRole.SYSTEM]
        max_len = self.generation_settings.max_history_length
        if filtered_history and filtered_history[-1].role == MessageRole.USER and \
        filtered_history[-1].content == current_content:
            filtered_history = filtered_history[:-1]

        filtered_history = filtered_history[-max_len:]

        history_messages = []

        for message in filtered_history:
            if message.role == MessageRole.SYSTEM:
                continue
            history_messages.append({"role": message.role, "content": message.content})

        return history_messages
    
    def build_openrouter_messages(
        self,
        chat: LlmChat,
        history: list[LlmMessage],
        current_content: str,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        system_prompt = self.build_system_prompt(chat)
        messages.append(
            {
                "role": MessageRole.SYSTEM.value,
                "content": system_prompt,
            }
        )

        trimmed_history = self.trim_history(
        history=history,
        current_content=current_content)

        messages.extend(trimmed_history)
        messages.append({"role": "user", "content": current_content})
        return messages
