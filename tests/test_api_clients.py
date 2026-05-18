import os
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from aeroplanes.api.base import AeroplanesAPIBase
from aeroplanes.api.clients import AeroplanesAPI
from aeroplanes.models import BoundingBox


class _Resp:
    def __init__(self, payload, *, status_code: int = 200, raise_exc: Exception | None = None, json_exc: Exception | None = None):
        self._payload = payload
        self.status_code = status_code
        self._raise_exc = raise_exc
        self._json_exc = json_exc

    def raise_for_status(self):
        if self._raise_exc is not None:
            raise self._raise_exc
        if self.status_code >= 400:
            raise requests.HTTPError("http error")

    def json(self):
        if self._json_exc is not None:
            raise self._json_exc
        return self._payload


def test_api_init_sets_default_user_agent() -> None:
    session = Mock()
    session.headers = {}
    AeroplanesAPI(session=session, user_agent="ua-test/1.0")
    assert session.headers["User-Agent"] == "ua-test/1.0"


def test_get_country_bbox_invalid_country() -> None:
    session = Mock()
    session.headers = {}
    api = AeroplanesAPI(session=session)
    with pytest.raises(ValueError):
        api.get_country_bbox("")


def test_get_country_bbox_request_error_wrapped() -> None:
    session = Mock()
    session.headers = {}
    session.get.side_effect = requests.RequestException("boom")
    api = AeroplanesAPI(session=session)
    with pytest.raises(RuntimeError, match="Failed to fetch bbox"):
        api.get_country_bbox("France")


def test_get_country_bbox_invalid_json_wrapped() -> None:
    session = Mock()
    session.headers = {}
    session.get.return_value = _Resp(None, json_exc=ValueError("bad json"))
    api = AeroplanesAPI(session=session)
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        api.get_country_bbox("France")


def test_get_country_bbox_missing_or_bad_bbox_shape() -> None:
    session = Mock()
    session.headers = {}
    api = AeroplanesAPI(session=session)

    session.get.return_value = _Resp([{"nope": []}])
    with pytest.raises(RuntimeError, match="boundingbox"):
        api.get_country_bbox("France")

    session.get.return_value = _Resp([{"boundingbox": ["1", "2", "3"]}])
    with pytest.raises(RuntimeError, match="boundingbox"):
        api.get_country_bbox("France")


def test_get_country_bbox_bad_bbox_values() -> None:
    session = Mock()
    session.headers = {}
    session.get.return_value = _Resp([{"boundingbox": ["a", "b", "c", "d"]}])
    api = AeroplanesAPI(session=session)
    with pytest.raises(RuntimeError, match="Invalid boundingbox"):
        api.get_country_bbox("France")


def test_get_aeroplanes_states_none_and_wrong_type() -> None:
    session = Mock()
    session.headers = {}
    api = AeroplanesAPI(session=session)
    api.get_country_bbox = Mock(return_value=BoundingBox(1, 2, 3, 4))  # type: ignore[method-assign]

    session.get.return_value = _Resp({"states": None})
    assert api.get_aeroplanes("France") == []

    session.get.return_value = _Resp({"states": "not-a-list"})
    with pytest.raises(RuntimeError, match="states"):
        api.get_aeroplanes("France")


def test_get_aeroplanes_request_error_wrapped() -> None:
    session = Mock()
    session.headers = {}
    api = AeroplanesAPI(session=session)
    api.get_country_bbox = Mock(return_value=BoundingBox(1, 2, 3, 4))  # type: ignore[method-assign]

    session.get.side_effect = requests.RequestException("boom")
    with pytest.raises(RuntimeError, match="Failed to fetch aeroplanes"):
        api.get_aeroplanes("France")


def test_get_aeroplanes_invalid_json_wrapped() -> None:
    session = Mock()
    session.headers = {}
    api = AeroplanesAPI(session=session)
    api.get_country_bbox = Mock(return_value=BoundingBox(1, 2, 3, 4))  # type: ignore[method-assign]

    session.get.return_value = _Resp(None, json_exc=ValueError("bad json"))
    with pytest.raises(RuntimeError, match="Invalid JSON"):
        api.get_aeroplanes("France")


def test_get_opensky_auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPEN_SKY_USERNAME", raising=False)
    monkeypatch.delenv("OPEN_SKY_PASSWORD", raising=False)
    assert AeroplanesAPI._get_opensky_auth() is None

    monkeypatch.setenv("OPEN_SKY_USERNAME", "u")
    monkeypatch.setenv("OPEN_SKY_PASSWORD", "p")
    assert AeroplanesAPI._get_opensky_auth() == ("u", "p")


def test_abstract_bases_raise_not_implemented() -> None:
    class _Dummy(AeroplanesAPIBase):
        def get_country_bbox(self, country: str) -> BoundingBox:  # pragma: no cover (impl not used)
            return AeroplanesAPIBase.get_country_bbox(self, country)

        def get_aeroplanes(self, country: str) -> list[list[object]]:  # pragma: no cover (impl not used)
            return AeroplanesAPIBase.get_aeroplanes(self, country)

    dummy = _Dummy()
    with pytest.raises(NotImplementedError):
        dummy.get_country_bbox("X")
    with pytest.raises(NotImplementedError):
        dummy.get_aeroplanes("X")

