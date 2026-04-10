from __future__ import annotations

from typing import Any
import httpx

class GeocodingError(Exception):
    """Базовая ошибка геокодирования."""


class AddressNotFoundError(GeocodingError):
    """Адрес не найден."""


async def geocode_address(
    *,
    api_key: str,
    country: str,
    city: str,
    street: str,
    house: str,
    lang: str = "ru_RU",
    timeout: int = 10,
) -> dict[str, Any]:
    address = f"{country}, {city}, {street}, {str(house).strip()}"

    url = "https://geocode-maps.yandex.ru/v1"
    params = {
        "apikey": api_key,
        "geocode": address,
        "lang": lang,
        "format": "json",
        "results": 1,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=timeout)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise GeocodingError(f"Geocoder response error: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise GeocodingError("Invalid JSON") from e

    try:
        members = data["response"]["GeoObjectCollection"]["featureMember"]
    except KeyError as e:
        raise GeocodingError("Wrong structure") from e

    if not members:
        raise AddressNotFoundError(f"Address not found: {address}")

    geo_object = members[0]["GeoObject"]

    try:
        pos = geo_object["Point"]["pos"]  # "lon lat"
        lon_str, lat_str = pos.split()
        lon = float(lon_str)
        lat = float(lat_str)
    except (KeyError, ValueError) as e:
        raise GeocodingError("Unable to get the responce") from e

    formatted_address = (
        geo_object.get("metaDataProperty", {})
        .get("GeocoderMetaData", {})
        .get("text")
    )

    precision = (
        geo_object.get("metaDataProperty", {})
        .get("GeocoderMetaData", {})
        .get("precision")
    )

    return {
        "address": address,
        "lat": lat,
        "lon": lon,
        "formatted_address": formatted_address,
        "precision": precision,
    }