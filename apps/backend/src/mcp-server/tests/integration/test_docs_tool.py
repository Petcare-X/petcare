"""
TC-03 · Инструмент «documents» — реальные данные из PostgreSQL + MinIO
"""

from __future__ import annotations

from datetime import date

import pytest

from tests.integration.conftest import TEST_DOCUMENT_CONTENT, TEST_DOCUMENT_CUSTOM_NAME


@pytest.mark.asyncio
async def test_get_pet_documents_from_db(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(f"/mcp/pets/{pet_id}/documents")
    assert response.status_code == 200, response.text
    docs = response.json()["data"]
    assert TEST_DOCUMENT_CUSTOM_NAME in [doc["custom_name"] for doc in docs]
    target = next(doc for doc in docs if doc["custom_name"] == TEST_DOCUMENT_CUSTOM_NAME)
    assert "document_type" in target


@pytest.mark.asyncio
async def test_get_pet_documents_by_date(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(
        f"/mcp/pets/{pet_id}/documents/by-date",
        params={"uploaded_at": date.today().isoformat()},
    )
    assert response.status_code == 200, response.text
    docs = response.json()["data"]
    assert TEST_DOCUMENT_CUSTOM_NAME in [doc["custom_name"] for doc in docs]


@pytest.mark.asyncio
async def test_get_pet_documents_by_date_wrong_format(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(
        f"/mcp/pets/{pet_id}/documents/by-date",
        params={"uploaded_at": "not-a-date"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_extract_document_text_from_s3(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.post(
        "/mcp/documents/extract",
        json={"pet_id": pet_id, "custom_name": TEST_DOCUMENT_CUSTOM_NAME},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["custom_name"] == TEST_DOCUMENT_CUSTOM_NAME
    assert data["parsed_text"] == TEST_DOCUMENT_CONTENT.decode("utf-8")


@pytest.mark.asyncio
async def test_extract_document_not_found(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.post(
        "/mcp/documents/extract",
        json={"pet_id": pet_id, "custom_name": "does-not-exist-at-all"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_extract_document_wrong_pet(client, seed_data):
    response = await client.post(
        "/mcp/documents/extract",
        json={"pet_id": 999999, "custom_name": TEST_DOCUMENT_CUSTOM_NAME},
    )
    assert response.status_code in (403, 404)


@pytest.mark.asyncio
async def test_documents_list_empty_for_past_date(client, seed_data):
    pet_id = seed_data["pet_id"]
    response = await client.get(
        f"/mcp/pets/{pet_id}/documents/by-date",
        params={"uploaded_at": "2000-01-01"},
    )
    assert response.status_code == 200
    assert response.json()["data"] == []
