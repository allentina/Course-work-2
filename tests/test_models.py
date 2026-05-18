import pytest

from aeroplanes.models import Aeroplane, BoundingBox


def test_bounding_box_validation() -> None:
    BoundingBox(1.0, 2.0, 3.0, 4.0)
    with pytest.raises(ValueError):
        BoundingBox(2.0, 1.0, 3.0, 4.0)
    with pytest.raises(ValueError):
        BoundingBox(1.0, 2.0, 5.0, 4.0)


def test_aeroplane_validation() -> None:
    a = Aeroplane("TEST1", "United States", 250.0, 10000.0, icao24="abc123")
    assert a.callsign == "TEST1"
    assert a.origin_country == "United States"

    with pytest.raises(ValueError):
        Aeroplane("", "X", 1.0, 1.0)
    with pytest.raises(ValueError):
        Aeroplane("A", "", 1.0, 1.0)
    with pytest.raises(ValueError):
        Aeroplane("A", "X", -1.0, 1.0)
    with pytest.raises(ValueError):
        Aeroplane("A", "X", 1.0, -5.0)


def test_aeroplane_comparisons() -> None:
    low = Aeroplane("LOW", "X", 100.0, 1000.0)
    high = Aeroplane("HIGH", "X", 90.0, 9000.0)
    fast = Aeroplane("FAST", "X", 300.0, 2000.0)

    assert low < high
    assert high.higher_than(low)
    assert fast.faster_than(low)


def test_from_opensky_state_handles_empty_callsign() -> None:
    state = ["abc123", None, "France", None, None, None, None, 1234.5, None, 200.0]
    a = Aeroplane.from_opensky_state(state)
    assert a.callsign
    assert a.origin_country == "France"
    assert a.velocity_mps == 200.0
    assert a.baro_altitude_m == 1234.5

