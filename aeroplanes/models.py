from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class BoundingBox:
    south_lat: float
    north_lat: float
    west_lon: float
    east_lon: float

    def __post_init__(self) -> None:
        if self.south_lat > self.north_lat:
            raise ValueError("south_lat must be <= north_lat")
        if self.west_lon > self.east_lon:
            raise ValueError("west_lon must be <= east_lon")


class Aeroplane:
    """
    Модель самолета по данным OpenSky.

    Минимальные атрибуты (>=4 по заданию):
    - callsign: позывной
    - origin_country: страна регистрации (как в OpenSky origin_country)
    - velocity_mps: скорость (м/с)
    - baro_altitude_m: высота (м), может быть None
    Дополнительно:
    - icao24: уникальный hex-идентификатор
    """

    __slots__ = ("_icao24", "_callsign", "_origin_country", "_velocity_mps", "_baro_altitude_m")

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity_mps: float,
        baro_altitude_m: Optional[float],
        icao24: str = "",
    ) -> None:
        self._icao24 = self._validate_str("icao24", icao24, allow_empty=True).lower()
        self._callsign = self._validate_str("callsign", callsign, allow_empty=False).strip()
        self._origin_country = self._validate_str("origin_country", origin_country, allow_empty=False).strip()
        self._velocity_mps = self._validate_float("velocity_mps", velocity_mps, min_value=0.0, allow_none=False)
        self._baro_altitude_m = self._validate_float(
            "baro_altitude_m", baro_altitude_m, min_value=0.0, allow_none=True
        )

    @staticmethod
    def _validate_str(name: str, value: Any, *, allow_empty: bool) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be str")
        if not allow_empty and not value.strip():
            raise ValueError(f"{name} must be non-empty")
        return value

    @staticmethod
    def _validate_float(
        name: str, value: Any, *, min_value: float, allow_none: bool
    ) -> Optional[float]:
        if value is None:
            if allow_none:
                return None
            raise TypeError(f"{name} must be a number, not None")
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be int/float")
        value_f = float(value)
        if value_f < min_value:
            raise ValueError(f"{name} must be >= {min_value}")
        return value_f

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity_mps(self) -> float:
        return self._velocity_mps

    @property
    def baro_altitude_m(self) -> Optional[float]:
        return self._baro_altitude_m

    # Сравнение по высоте (по умолчанию): None считается как 0 для сравнения
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self.baro_altitude_m or 0.0) < (other.baro_altitude_m or 0.0)

    def higher_than(self, other: "Aeroplane") -> bool:
        return (self.baro_altitude_m or 0.0) > (other.baro_altitude_m or 0.0)

    def faster_than(self, other: "Aeroplane") -> bool:
        return self.velocity_mps > other.velocity_mps

    def to_dict(self) -> dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity_mps": self.velocity_mps,
            "baro_altitude_m": self.baro_altitude_m,
        }

    @classmethod
    def from_opensky_state(cls, state: list[Any]) -> "Aeroplane":
        """
        OpenSky states: https://openskynetwork.github.io/opensky-api/rest.html
        Индексы в массиве state (важные для нас):
        0 icao24
        1 callsign
        2 origin_country
        9 velocity (m/s)
        7 baro_altitude (m)
        """
        icao24 = state[0] or ""
        callsign = (state[1] or "").strip()
        origin_country = state[2] or ""
        baro_altitude = state[7]
        velocity = state[9]

        # В OpenSky callsign бывает пустым; чтобы не падать на валидации,
        # подставим icao24 как минимально идентифицирующее значение.
        if not callsign:
            callsign = str(icao24) or "UNKNOWN"

        return cls(
            icao24=str(icao24),
            callsign=str(callsign),
            origin_country=str(origin_country),
            velocity_mps=float(velocity) if velocity is not None else 0.0,
            baro_altitude_m=float(baro_altitude) if baro_altitude is not None else None,
        )

    @classmethod
    def cast_to_object_list(cls, raw: list[list[Any]]) -> list["Aeroplane"]:
        return [cls.from_opensky_state(s) for s in raw]

