from unittest.mock import Mock

import pytest

from aeroplanes.api.clients import AeroplanesAPI


class _Resp:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("http error")

    def json(self):
        return self._payload


def test_get_country_bbox_parses_boundingbox() -> None:
    session = Mock()
    session.headers = {}
    session.get.return_value = _Resp([{"boundingbox": ["1", "2", "3", "4"]}])

    api = AeroplanesAPI(session=session)
    bbox = api.get_country_bbox("Canada")
    assert bbox.south_lat == 1.0
    assert bbox.north_lat == 2.0
    assert bbox.west_lon == 3.0
    assert bbox.east_lon == 4.0


def test_get_country_bbox_not_found() -> None:
    session = Mock()
    session.headers = {}
    session.get.return_value = _Resp([])
    api = AeroplanesAPI(session=session)
    with pytest.raises(LookupError):
        api.get_country_bbox("NoSuchCountry")

