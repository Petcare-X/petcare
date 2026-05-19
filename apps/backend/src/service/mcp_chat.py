from src.clients.mcp_client import MCPClient


class MCPChatService:
    def __init__(self) -> None:
        self.client = MCPClient()

    async def generate_petcare_answer(
        self,
        message: str,
        user_id: int,
        pet_id: int | None = None,
    ) -> str:
        result = await self.client.ask_assistant(
            question=message,
            user_id=user_id,
            pet_id=pet_id,
            include_documents=True,
        )

        data = result.get("data")
        if not data:
            error = result.get("error") or {}
            raise RuntimeError(error.get("message", "MCP service returned empty response"))

        return data["answer"]
