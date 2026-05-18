from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Optional

from aeroplanes.models import Aeroplane


Criteria = Optional[Callable[[dict[str, Any]], bool]]


class AeroplaneStorageBase(ABC):
    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_aeroplanes(self, criteria: Criteria = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def delete_aeroplanes(self, criteria: Criteria = None) -> int:
        raise NotImplementedError

    # Заглушки "на будущее" под БД/удаленные хранилища:
    @abstractmethod
    def update_aeroplanes(self, criteria: Criteria, patch: dict[str, Any]) -> int:
        raise NotImplementedError

    @abstractmethod
    def bulk_add(self, aeroplanes: Iterable[Aeroplane]) -> int:
        raise NotImplementedError

