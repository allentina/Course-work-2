from __future__ import annotations

from aeroplanes.api.clients import AeroplanesAPI
from aeroplanes.models import Aeroplane
from aeroplanes.services import (
    filter_by_altitude_range,
    filter_by_registration_country,
    format_aeroplane,
    top_n_by_altitude,
)
from aeroplanes.storage.json_saver import JSONSaver


def user_interaction() -> None:
    api = AeroplanesAPI()
    storage = JSONSaver()

    aeroplanes: list[Aeroplane] = []

    while True:
        print()
        print("1. Загрузить самолеты по стране (OpenSky + Nominatim)")
        print("2. Показать топ N по высоте (DESC)")
        print("3. Фильтр по стране регистрации")
        print("4. Фильтр по диапазону высоты (м)")
        print("5. Сохранить текущий список в JSON")
        print("6. Показать, что в JSON (файл-хранилище)")
        print("7. Очистить JSON")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                country = input("Введите название страны: ").strip()
                raw_states = api.get_aeroplanes(country)
                aeroplanes = Aeroplane.cast_to_object_list(raw_states)
                print(f"Загружено самолетов: {len(aeroplanes)}")
            elif choice == "2":
                n = int(input("Введите N: ").strip())
                for a in top_n_by_altitude(aeroplanes, n):
                    print(format_aeroplane(a))
            elif choice == "3":
                reg = input("Введите страну регистрации (origin_country): ").strip()
                filtered = filter_by_registration_country(aeroplanes, reg)
                print(f"Найдено: {len(filtered)}")
                for a in filtered[:50]:
                    print(format_aeroplane(a))
            elif choice == "4":
                raw = input("Введите диапазон (пример: 1000-12000) или пусто: ").strip()
                if not raw:
                    min_alt = None
                    max_alt = None
                else:
                    parts = [p.strip() for p in raw.replace(" ", "").split("-", 1)]
                    if len(parts) != 2:
                        raise ValueError("Нужен диапазон вида min-max")
                    min_alt = float(parts[0]) if parts[0] else None
                    max_alt = float(parts[1]) if parts[1] else None
                filtered = filter_by_altitude_range(aeroplanes, min_alt_m=min_alt, max_alt_m=max_alt)
                print(f"Найдено: {len(filtered)}")
                for a in top_n_by_altitude(filtered, min(20, len(filtered)) or 1):
                    print(format_aeroplane(a))
            elif choice == "5":
                saved = storage.bulk_add(aeroplanes)
                print(f"Сохранено: {saved}")
            elif choice == "6":
                rows = storage.get_aeroplanes()
                print(f"Записей в файле: {len(rows)}")
                for row in rows[:20]:
                    print(row)
            elif choice == "7":
                deleted = storage.delete_aeroplanes()
                print(f"Удалено: {deleted}")
            elif choice == "0":
                return
            else:
                print("Неизвестная команда")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    user_interaction()
