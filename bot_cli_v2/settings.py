from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Глобальні налаштування проєкту."""

    # Політика дублікатів
    allow_duplicate_phones: bool = False

    # Автодопомога після N порожніх Enter
    auto_help_every_empty_inputs: int = 6

    # Підтвердження небезпечних дій (remove/delete)
    require_remove_confirmation: bool = True
    remove_confirm_word: str = "YES"

    # Нормалізація телефонів
    # Якщо номер починається з 0 (локальний формат) — підставляємо код країни
    default_country_code: str = "+38"  # можеш змінити на "+353" для Ірландії

    # Файли даних
    contacts_json_name: str = "contacts.json"
    contacts_txt_name: str = "contacts.txt"  # для міграції, якщо існує

    # Експорт/імпорт
    export_default_name: str = "contacts_export.csv"


SETTINGS = Settings()