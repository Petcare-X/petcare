import asyncio

import httpx

from src.core.config import settings
from src.core.security import create_access_token


class MCPClient:
    async def ask_assistant(
        self,
        question: str,
        user_id: int,
        pet_id: int | None = None,
        include_documents: bool = True,
    ) -> dict:
        if not settings.MCP_SERVICE_URL:
            raise RuntimeError("MCP_SERVICE_URL is not configured")

        payload = {
            "tool": "assistant",
            "method": "ask_petcare_assistant",
            "payload": {
                "question": question,
                "user_id": str(user_id),
                "pet_id": pet_id,
                "include_documents": include_documents,
            },
        }

        for attempt in range(1, settings.MCP_MAX_REQUEST_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.MCP_CLIENT_TIMEOUT_SECONDS) as client:
                    response = await client.post(
                        f"{settings.MCP_SERVICE_URL}/mcp/execute",
                        json=payload,
                        headers={"Authorization": f"Bearer {create_access_token(user_id)}"},
                    )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                if attempt == settings.MCP_MAX_REQUEST_ATTEMPTS:
                    raise
                await asyncio.sleep(settings.MCP_RETRY_DELAY_SECONDS)
