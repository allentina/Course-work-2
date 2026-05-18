from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from aeroplanes.models import Aeroplane
from aeroplanes.storage.base import AeroplaneStorageBase, Criteria


class JSONSaver(AeroplaneStorageBase):
    def __init__(self, path: str | Path = Path("data") / "aeroplanes.json") -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._read()
        data.append(aeroplane.to_dict())
        self._write(data)

    def get_aeroplanes(self, criteria: Criteria = None) -> list[dict[str, Any]]:
        data = self._read()
        if criteria is None:
            return data
        return [row for row in data if criteria(row)]

    def delete_aeroplanes(self, criteria: Criteria = None) -> int:
        data = self._read()
        if criteria is None:
            deleted = len(data)
            self._write([])
            return deleted

        kept: list[dict[str, Any]] = []
        deleted = 0
        for row in data:
            if criteria(row):
                deleted += 1
            else:
                kept.append(row)
        self._write(kept)
        return deleted

    def update_aeroplanes(self, criteria: Criteria, patch: dict[str, Any]) -> int:
        # Заглушка под БД: для JSON тоже можно поддержать, но по заданию не обязательно.
        if criteria is None:
            return 0
        data = self._read()
        updated = 0
        for row in data:
            if criteria(row):
                row.update(patch)
                updated += 1
        self._write(data)
        return updated

    def bulk_add(self, aeroplanes: Iterable[Aeroplane]) -> int:
        data = self._read()
        items = [a.to_dict() for a in aeroplanes]
        data.extend(items)
        self._write(data)
        return len(items)

    def _read(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        try:
            raw = self._path.read_text(encoding="utf-8")
            if not raw.strip():
                return []
            data = json.loads(raw)
        except OSError as e:
            raise RuntimeError(f"Failed to read JSON file: {self._path}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in file: {self._path}") from e

        if not isinstance(data, list):
            raise RuntimeError(f"JSON root must be list: {self._path}")
        out: list[dict[str, Any]] = []
        for row in data:
            if isinstance(row, dict):
                out.append(row)
        return out

    def _write(self, data: list[dict[str, Any]]) -> None:
        try:
            self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as e:
            raise RuntimeError(f"Failed to write JSON file: {self._path}") from e

