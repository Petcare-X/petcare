import httpx

from src.core.config import settings


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

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.MCP_SERVICE_URL}/mcp/execute",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
