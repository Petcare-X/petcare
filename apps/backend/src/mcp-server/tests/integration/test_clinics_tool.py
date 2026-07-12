"""
TC-04 · Инструмент «clinics» — реальные данные из PostgreSQL
"""

from __future__ import annotations

import pytest

from tests.integration.conftest import TEST_CLINIC_CITY, TEST_CLINIC_NAME


@pytest.mark.asyncio
async def test_search_clinics_by_city(client, seed_data):
    response = await client.get("/mcp/clinics/city", params={"vet_city": TEST_CLINIC_CITY})
    assert response.status_code == 200, response.text
    clinics = response.json()["data"]
    assert TEST_CLINIC_NAME in [clinic["vet_name"] for clinic in clinics]


@pytest.mark.asyncio
async def test_search_clinics_city_case_insensitive(client, seed_data):
    upper_response = await client.get("/mcp/clinics/city", params={"vet_city": TEST_CLINIC_CITY.upper()})
    lower_response = await client.get("/mcp/clinics/city", params={"vet_city": TEST_CLINIC_CITY.lower()})
    assert upper_response.status_code == 200
    assert lower_response.status_code == 200
    assert upper_response.json()["data"] == lower_response.json()["data"]


@pytest.mark.asyncio
async def test_search_clinics_city_not_found(client):
    response = await client.get("/mcp/clinics/city", params={"vet_city": "CityThatDoesNotExist12345"})
    assert response.status_code == 200
    assert response.json()["data"] == []


@pytest.mark.asyncio
async def test_search_clinics_by_location(client, seed_data):
    response = await client.get(
        "/mcp/clinics/location",
        params={"user_lat": 55.7558, "user_lon": 37.6176, "radius_km": 5.0},
    )
    assert response.status_code == 200, response.text
    clinics = response.json()["data"]
    assert TEST_CLINIC_NAME in [clinic["vet_name"] for clinic in clinics]
    distances = [clinic["distance_km"] for clinic in clinics]
    assert distances == sorted(distances)
    target = next(clinic for clinic in clinics if clinic["vet_name"] == TEST_CLINIC_NAME)
    assert target["distance_km"] < 0.1


@pytest.mark.asyncio
async def test_search_clinics_by_location_outside_radius(client, seed_data):
    response = await client.get(
        "/mcp/clinics/location",
        params={"user_lat": 43.1155, "user_lon": 131.8855, "radius_km": 10.0},
    )
    assert response.status_code == 200
    assert TEST_CLINIC_NAME not in [clinic["vet_name"] for clinic in response.json()["data"]]


@pytest.mark.asyncio
async def test_filter_available_clinics_open_now(client, seed_data):
    response = await client.post(
        "/mcp/clinics/filter-available",
        json={"vet_city": TEST_CLINIC_CITY, "current_datetime": "2026-05-08T12:00:00"},
    )
    assert response.status_code == 200, response.text
    clinics = response.json()["data"]
    assert TEST_CLINIC_NAME in [clinic["vet_name"] for clinic in clinics]


@pytest.mark.asyncio
async def test_filter_available_clinics_closed(client, seed_data):
    response = await client.post(
        "/mcp/clinics/filter-available",
        json={"vet_city": TEST_CLINIC_CITY, "current_datetime": "2026-05-08T23:00:00"},
    )
    assert response.status_code == 200
    assert TEST_CLINIC_NAME not in [clinic["vet_name"] for clinic in response.json()["data"]]


@pytest.mark.asyncio
async def test_get_vet_contacts(client, seed_data):
    clinic_id = seed_data["clinic_id"]
    response = await client.get(f"/mcp/clinics/{clinic_id}/contacts")
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["vet_phone"] == "+7-999-000-00-01"
    assert data["vet_website"] == "https://integration-vet.example.com"


@pytest.mark.asyncio
async def test_get_vet_contacts_not_found(client):
    response = await client.get("/mcp/clinics/999999/contacts")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_vet_location_by_name(client, seed_data):
    response = await client.get(
        "/mcp/clinics/location-by-name",
        params={"vet_name": TEST_CLINIC_NAME, "vet_city": TEST_CLINIC_CITY},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert abs(float(data["vet_lat"]) - 55.7558) < 0.001
    assert abs(float(data["vet_lon"]) - 37.6176) < 0.001


@pytest.mark.asyncio
async def test_get_vet_location_not_found(client):
    response = await client.get(
        "/mcp/clinics/location-by-name",
        params={"vet_name": "NoSuchClinic", "vet_city": "NoSuchCity"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
