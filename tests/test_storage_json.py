from pathlib import Path

from aeroplanes.models import Aeroplane
from aeroplanes.storage.json_saver import JSONSaver


def test_json_saver_add_get_delete(tmp_path: Path) -> None:
    path = tmp_path / "aeroplanes.json"
    saver = JSONSaver(path)

    a1 = Aeroplane("A1", "France", 100.0, 1000.0, icao24="aaa")
    a2 = Aeroplane("A2", "Germany", 200.0, 2000.0, icao24="bbb")
    saver.add_aeroplane(a1)
    saver.add_aeroplane(a2)

    rows = saver.get_aeroplanes()
    assert len(rows) == 2

    deleted = saver.delete_aeroplanes(lambda r: r.get("origin_country") == "France")
    assert deleted == 1
    rows2 = saver.get_aeroplanes()
    assert len(rows2) == 1
    assert rows2[0]["callsign"] == "A2"

