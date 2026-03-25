import httpx
from fastapi import HTTPException

from src.core.config import settings


class OpenRouterService:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_answer(self, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": user_message}
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter API error: {response.text}"
            )

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise HTTPException(status_code=502, detail="Invalid response from OpenRouter")