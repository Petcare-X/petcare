import asyncio
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.core.exceptions import ValidationAppError
from app.core.prompt_loader import load_system_prompt
from app.llm.base import LLMAdapter


class OpenRouterAdapter(LLMAdapter):
    name = "openrouter"

    async def complete(self, prompt: str, context: Dict[str, Any] | None = None) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise ValidationAppError("OpenRouter API key is not configured")
        if not settings.OPENROUTER_MODEL:
            raise ValidationAppError("OpenRouter model is not configured")

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        system_prompt = load_system_prompt()
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
            "top_p": 0.8,
        }
        timeout = httpx.Timeout(settings.OPENROUTER_TIMEOUT_SECONDS)

        for attempt in range(1, settings.OPENROUTER_MAX_REQUEST_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        settings.OPENROUTER_BASE_URL,
                        headers=headers,
                        json=payload,
                    )
                break
            except httpx.RequestError as exc:
                if attempt == settings.OPENROUTER_MAX_REQUEST_ATTEMPTS:
                    raise ValidationAppError(f"OpenRouter request failed: {exc}") from exc
                await asyncio.sleep(settings.OPENROUTER_RETRY_DELAY_SECONDS)

        if response.status_code >= 400:
            raise ValidationAppError(f"OpenRouter API error: {response.text}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValidationAppError("OpenRouter response did not contain generated text") from exc
