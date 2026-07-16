from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings


NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/search"
)

# left, top, right, bottom
ALMATY_VIEWBOX = (
    "76.70,43.40,"
    "77.20,43.05"
)

ALMATY_MIN_LAT = Decimal("43.05")
ALMATY_MAX_LAT = Decimal("43.40")

ALMATY_MIN_LON = Decimal("76.70")
ALMATY_MAX_LON = Decimal("77.20")


class GeocodingError(Exception):
    """Raised when geocoding fails."""


def is_inside_almaty(latitude, longitude):
    """
    Return True if coordinates are
    inside the Almaty area.
    """

    return (
        ALMATY_MIN_LAT <= latitude <= ALMATY_MAX_LAT
        and
        ALMATY_MIN_LON <= longitude <= ALMATY_MAX_LON
    )


def geocode_location(location_name):
    """
    Convert a location name
    into latitude and longitude.
    """

    if not location_name.strip():
        raise GeocodingError(
            "Location cannot be empty."
        )

    params = {
        "q": f"{location_name}, Almaty, Kazakhstan",
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "kz",
        "viewbox": ALMATY_VIEWBOX,
        "bounded": 1,
    }

    headers = {
        "User-Agent": settings.GEOCODING_USER_AGENT,
    }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise GeocodingError(
            "Geocoding service unavailable."
        ) from exc

    results = response.json()

    if not results:
        raise GeocodingError(
            f'"{location_name}" not found.'
        )

    try:
        latitude = Decimal(results[0]["lat"])
        longitude = Decimal(results[0]["lon"])

    except (
        KeyError,
        InvalidOperation,
    ) as exc:
        raise GeocodingError(
            "Invalid location data."
        ) from exc

    if not is_inside_almaty(
        latitude,
        longitude,
    ):
        raise GeocodingError(
            "Location must be inside Almaty."
        )

    return (
        latitude,
        longitude,
    )
