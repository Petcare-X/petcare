"""
TC-01 · Доступность MCP-эндпоинта

Проверяем, что:
  - сервер отвечает
  - /docs возвращает HTML
  - /auth/login работает корректно
  - невалидный токен отклоняется с 403
  - отсутствие токена отклоняется с 403
"""

from __future__ import annotations

import httpx
import pytest

from tests.integration.conftest import AUTH_PASSWORD, BASE_URL, TEST_USER_ID


@pytest.mark.asyncio
async def test_server_is_reachable():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_success():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.post(
            "/auth/login",
            json={"user_id": TEST_USER_ID, "password": AUTH_PASSWORD},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    parts = body["data"]["access_token"].split(".")
    assert len(parts) == 3
    assert body["data"]["token_type"] == "bearer"
    assert isinstance(body["data"]["expires_in_minutes"], int)


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.post(
            "/auth/login",
            json={"user_id": TEST_USER_ID, "password": "wrong-password"},
        )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.get("/mcp/pets/1/details")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_protected_endpoint_with_bad_token():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.get(
            "/mcp/pets/1/details",
            headers={"Authorization": "Bearer totally.invalid.token"},
        )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_openapi_schema_has_mcp_routes():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5) as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})
    expected = [
        "/auth/login",
        "/mcp/pets/{pet_id}/details",
        "/mcp/pets/{pet_id}/short",
        "/mcp/pets/{pet_id}/documents",
        "/mcp/clinics/city",
        "/mcp/execute",
    ]
    for path in expected:
        assert path in paths
