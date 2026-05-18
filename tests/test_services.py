import pytest

from aeroplanes.models import Aeroplane
from aeroplanes.services import (
    filter_by_altitude_range,
    filter_by_registration_country,
    top_n_by_altitude,
)


def _planes():
    return [
        Aeroplane("A", "France", 100.0, 1000.0),
        Aeroplane("B", "France", 120.0, 5000.0),
        Aeroplane("C", "Germany", 90.0, None),
        Aeroplane("D", "Germany", 200.0, 8000.0),
    ]


def test_top_n_by_altitude_desc() -> None:
    planes = _planes()
    top = top_n_by_altitude(planes, 2)
    assert [p.callsign for p in top] == ["D", "B"]


def test_filter_by_country() -> None:
    planes = _planes()
    fr = filter_by_registration_country(planes, "france")
    assert {p.callsign for p in fr} == {"A", "B"}


def test_filter_by_altitude_range() -> None:
    planes = _planes()
    out = filter_by_altitude_range(planes, min_alt_m=2000, max_alt_m=7000)
    assert {p.callsign for p in out} == {"B"}

    with pytest.raises(ValueError):
        filter_by_altitude_range(planes, min_alt_m=10, max_alt_m=1)

