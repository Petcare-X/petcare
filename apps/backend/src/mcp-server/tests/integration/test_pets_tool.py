"""
TC-02 · Инструмент «pets» — реальные данные из PostgreSQL
"""

from __future__ import annotations

import pytest

from tests.integration.conftest import TEST_PET_NAME


@pytest.mark.asyncio
async def test_get_pet_details_returns_db_data(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(f"/mcp/pets/{pet_id}/details")
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["pet_name"] == TEST_PET_NAME
    assert data["animal_breed"] == "Labrador"
    assert isinstance(data["age"], int)
    assert data["age"] >= 4
    assert "pet_weight" in data
    assert "pet_is_sterylyzed" in data


@pytest.mark.asyncio
async def test_get_pet_details_data_is_live(client, seed_data):
    pet_id = seed_data["pet_id"]
    first = await client.get(f"/mcp/pets/{pet_id}/details")
    second = await client.get(f"/mcp/pets/{pet_id}/details")
    assert first.json()["data"] == second.json()["data"]


@pytest.mark.asyncio
async def test_get_pet_short_info(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(f"/mcp/pets/{pet_id}/short")
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["pet_name"] == TEST_PET_NAME
    assert data["animal_type"] == "Dog"
    assert data["animal_breed"] == "Labrador"
    assert isinstance(data["age"], int)


@pytest.mark.asyncio
async def test_get_pet_details_not_found(client):
    response = await client.get("/mcp/pets/999999/details")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_pet_details_forbidden_other_user(client, seed_data):
    candidate = 1 if seed_data["pet_id"] != 1 else 2
    response = await client.get(f"/mcp/pets/{candidate}/details")
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_mcp_execute_pets_details(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.post(
        "/mcp/execute",
        json={"tool": "pets", "method": "get_pet_short_info", "payload": {"pet_id": pet_id}},
    )
    assert response.status_code == 200, response.text
    assert response.json()["data"]["pet_name"] == TEST_PET_NAME


@pytest.mark.asyncio
async def test_mcp_execute_unknown_tool(client):
    response = await client.post(
        "/mcp/execute",
        json={"tool": "nonexistent_tool", "method": "something", "payload": {}},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_mcp_execute_unknown_method(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.post(
        "/mcp/execute",
        json={"tool": "pets", "method": "delete_all_pets", "payload": {"pet_id": pet_id}},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
