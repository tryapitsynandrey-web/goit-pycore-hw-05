# storage.py
"""Шар збереження AddressBook.

- JSON як основний формат (contacts.json)
- атомарне збереження через тимчасовий файл і replace()
- міграція з legacy contacts.txt (один раз)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from address_book import AddressBook


def load_address_book(
    *,
    json_path: Path,
    legacy_txt_path: Path,
    allow_duplicate_phones: bool,
) -> AddressBook:
    """Завантажує AddressBook з JSON, або мігрує з TXT, або створює порожню."""
    if json_path.exists():
        data = _read_json(json_path)
        book = AddressBook.from_dict(data, allow_duplicate_phones=allow_duplicate_phones)
        return book

    if legacy_txt_path.exists():
        book = _migrate_from_txt(
            txt_path=legacy_txt_path,
            allow_duplicate_phones=allow_duplicate_phones,
        )
        # Після міграції одразу зберігаємо у JSON
        save_address_book(json_path, book)
        book.is_dirty = False
        return book

    return AddressBook(allow_duplicate_phones=allow_duplicate_phones)


def save_address_book(json_path: Path, book: AddressBook) -> None:
    """Зберігає AddressBook у JSON атомарно."""
    json_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = json_path.with_suffix(".json.tmp")

    payload: Dict[str, Dict[str, str]] = book.to_dict()

    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.replace(json_path)
    book.is_dirty = False


def _read_json(path: Path) -> Dict[str, Dict[str, str]]:
    """Читає JSON у dict."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        return {}
    return data  # type: ignore[return-value]


def _migrate_from_txt(*, txt_path: Path, allow_duplicate_phones: bool) -> AddressBook:
    """Міграція з contacts.txt у AddressBook.

    Формат рядка:
    name: phone
    """
    book = AddressBook(allow_duplicate_phones=allow_duplicate_phones)
    for raw_line in txt_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            continue

        name_part, phone_part = line.split(":", 1)
        name = name_part.strip()
        phone = phone_part.strip()

        try:
            book.add(name=name, phone=phone)
        except (ValueError, KeyError):
            # Некоректні або дубльовані рядки — пропускаємо
            continue

    book.is_dirty = True
    return book