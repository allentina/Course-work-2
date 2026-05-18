from __future__ import annotations

import os
from typing import Any, Optional

import requests

from aeroplanes.api.base import AeroplanesAPIBase
from aeroplanes.models import BoundingBox


class AeroplanesAPI(AeroplanesAPIBase):
    """
    Интеграция:
    - Nominatim (OpenStreetMap) для bounding box страны
    - OpenSky для списка самолетов в bbox
    """

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        nominatim_base_url: str = "https://nominatim.openstreetmap.org",
        opensky_base_url: str = "https://opensky-network.org",
        user_agent: str = "coursework-aeroplanes/1.0 (requests)",
        timeout_s: float = 20.0,
    ) -> None:
        self._session = session or requests.Session()
        self._nominatim_base_url = nominatim_base_url.rstrip("/")
        self._opensky_base_url = opensky_base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._session.headers.setdefault("User-Agent", user_agent)

    def get_country_bbox(self, country: str) -> BoundingBox:
        if not isinstance(country, str) or not country.strip():
            raise ValueError("country must be a non-empty string")

        url = f"{self._nominatim_base_url}/search"
        params = {
            "q": country,
            "format": "json",
            "limit": 1,
            "addressdetails": 0,
        }
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout_s)
            resp.raise_for_status()
            data: list[dict[str, Any]] = resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch bbox from Nominatim: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON from Nominatim: {e}") from e

        if not data:
            raise LookupError(f"Country not found in Nominatim: {country}")

        item = data[0]
        bbox = item.get("boundingbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            raise RuntimeError("Nominatim response does not contain boundingbox[4]")

        # Nominatim: [south, north, west, east] as strings
        try:
            south, north, west, east = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        except (TypeError, ValueError) as e:
            raise RuntimeError(f"Invalid boundingbox values: {bbox}") from e

        return BoundingBox(south_lat=south, north_lat=north, west_lon=west, east_lon=east)

    def get_aeroplanes(self, country: str) -> list[list[object]]:
        bbox = self.get_country_bbox(country)
        url = f"{self._opensky_base_url}/api/states/all"
        params = {
            "lamin": bbox.south_lat,
            "lomin": bbox.west_lon,
            "lamax": bbox.north_lat,
            "lomax": bbox.east_lon,
        }

        auth = self._get_opensky_auth()
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout_s, auth=auth)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch aeroplanes from OpenSky: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON from OpenSky: {e}") from e

        states = data.get("states")
        if states is None:
            return []
        if not isinstance(states, list):
            raise RuntimeError("OpenSky response 'states' is not a list")
        return states

    @staticmethod
    def _get_opensky_auth() -> Optional[tuple[str, str]]:
        user = os.getenv("OPEN_SKY_USERNAME")
        password = os.getenv("OPEN_SKY_PASSWORD")
        if user and password:
            return (user, password)
        return None

