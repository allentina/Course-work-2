from __future__ import annotations

from abc import ABC, abstractmethod

from aeroplanes.models import BoundingBox


class AeroplanesAPIBase(ABC):
    @abstractmethod
    def get_country_bbox(self, country: str) -> BoundingBox:
        raise NotImplementedError

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[list[object]]:
        """
        Возвращает "states" (как в OpenSky): список массивов.
        Дальше это преобразуется в Aeroplane.cast_to_object_list(...)
        """
        raise NotImplementedError

