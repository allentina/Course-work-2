from __future__ import annotations

from typing import Iterable, Optional

from aeroplanes.models import Aeroplane


def top_n_by_altitude(aeroplanes: Iterable[Aeroplane], n: int) -> list[Aeroplane]:
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive int")
    return sorted(aeroplanes, key=lambda a: (a.baro_altitude_m or 0.0), reverse=True)[:n]


def filter_by_registration_country(aeroplanes: Iterable[Aeroplane], country: str) -> list[Aeroplane]:
    if not isinstance(country, str) or not country.strip():
        raise ValueError("country must be a non-empty string")
    needle = country.strip().casefold()
    return [a for a in aeroplanes if a.origin_country.casefold() == needle]


def filter_by_altitude_range(
    aeroplanes: Iterable[Aeroplane],
    *,
    min_alt_m: Optional[float] = None,
    max_alt_m: Optional[float] = None,
) -> list[Aeroplane]:
    if min_alt_m is not None and min_alt_m < 0:
        raise ValueError("min_alt_m must be >= 0")
    if max_alt_m is not None and max_alt_m < 0:
        raise ValueError("max_alt_m must be >= 0")
    if min_alt_m is not None and max_alt_m is not None and min_alt_m > max_alt_m:
        raise ValueError("min_alt_m must be <= max_alt_m")

    out: list[Aeroplane] = []
    for a in aeroplanes:
        alt = a.baro_altitude_m
        if alt is None:
            continue
        if min_alt_m is not None and alt < min_alt_m:
            continue
        if max_alt_m is not None and alt > max_alt_m:
            continue
        out.append(a)
    return out


def format_aeroplane(a: Aeroplane) -> str:
    alt = f"{a.baro_altitude_m:.0f} m" if a.baro_altitude_m is not None else "N/A"
    return f"{a.callsign} | {a.origin_country} | v={a.velocity_mps:.1f} m/s | alt={alt}"

