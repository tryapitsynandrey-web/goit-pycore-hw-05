# address_book.py
"""AddressBook — мінімальний клас адресної книги з політиками валідації.

Завдання:
- інкапсуляція dict
- add/change/remove/get/all/search/rename/stats
- нормалізація телефону у міжнародний формат +XXXXXXXX...
- політика дублікатів телефонів (allow_duplicate_phones)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from utils import normalize_phone, validate_name

def _now_iso() -> str:
    """Повертає поточний час в ISO-форматі (UTC)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Contact:
    """Модель контакту."""
    name: str
    phone: str
    created_at: str
    updated_at: str


class AddressBook:
    """Адресна книга з базовими операціями та валідацією."""

    def __init__(self, *, allow_duplicate_phones: bool = False) -> None:
        self._contacts: Dict[str, Contact] = {}
        self.allow_duplicate_phones = allow_duplicate_phones
        self.is_dirty: bool = False
        self._last_modified: Optional[str] = None

    # -------------------------
    # Службові методи
    # -------------------------

    def _touch(self) -> None:
        """Позначає, що книга змінена."""
        self.is_dirty = True
        self._last_modified = _now_iso()

    def _has_phone(self, phone: str, *, except_name: str | None = None) -> bool:
        """Перевіряє, чи телефон вже існує."""
        for name, c in self._contacts.items():
            if except_name is not None and name == except_name:
                continue
            if c.phone == phone:
                return True
        return False

    # -------------------------
    # Публічний API
    # -------------------------

    def add(self, *, name: str, phone: str) -> None:
        """Додає контакт. Підіймає ValueError/KeyError у разі проблем."""
        clean_name = validate_name(name)
        clean_phone = normalize_phone(phone)

        if clean_name in self._contacts:
            raise ValueError("Duplicate name")

        if not self.allow_duplicate_phones and self._has_phone(clean_phone):
            raise ValueError("Duplicate phone")

        now = _now_iso()
        self._contacts[clean_name] = Contact(
            name=clean_name,
            phone=clean_phone,
            created_at=now,
            updated_at=now,
        )
        self._touch()

    def change(self, *, name: str, phone: str) -> None:
        """Оновлює телефон контакту."""
        clean_name = validate_name(name)
        clean_phone = normalize_phone(phone)

        if clean_name not in self._contacts:
            raise KeyError(clean_name)

        if not self.allow_duplicate_phones and self._has_phone(clean_phone, except_name=clean_name):
            raise ValueError("Duplicate phone")

        c = self._contacts[clean_name]
        c.phone = clean_phone
        c.updated_at = _now_iso()
        self._touch()

    def remove(self, name: str) -> None:
        """Видаляє контакт."""
        clean_name = validate_name(name)
        if clean_name not in self._contacts:
            raise KeyError(clean_name)
        del self._contacts[clean_name]
        self._touch()

    def rename(self, *, old_name: str, new_name: str) -> None:
        """Перейменовує контакт."""
        old_clean = validate_name(old_name)
        new_clean = validate_name(new_name)

        if old_clean not in self._contacts:
            raise KeyError(old_clean)
        if new_clean in self._contacts:
            raise ValueError("Duplicate name")

        c = self._contacts.pop(old_clean)
        c.name = new_clean
        c.updated_at = _now_iso()
        self._contacts[new_clean] = c
        self._touch()

    def get(self, name: str) -> Dict[str, str]:
        """Повертає контакт як dict."""
        clean_name = validate_name(name)
        if clean_name not in self._contacts:
            raise KeyError(clean_name)
        c = self._contacts[clean_name]
        return {"name": c.name, "phone": c.phone}

    def all(self) -> List[Dict[str, str]]:
        """Повертає всі контакти (відсортовано за ім'ям)."""
        out: List[Dict[str, str]] = []
        for name in sorted(self._contacts.keys(), key=lambda s: s.casefold()):
            c = self._contacts[name]
            out.append({"name": c.name, "phone": c.phone})
        return out

    def search(self, query: str) -> List[Dict[str, str]]:
        """Пошук за ім'ям або телефоном (частковий збіг)."""
        q = query.strip()
        if not q:
            raise ValueError("Empty query")

        q_fold = q.casefold()
        out: List[Dict[str, str]] = []

        for c in self._contacts.values():
            if q_fold in c.name.casefold() or q_fold in c.phone.casefold():
                out.append({"name": c.name, "phone": c.phone})

        out.sort(key=lambda x: x["name"].casefold())
        return out

    def stats(self) -> Dict[str, str | int]:
        """Повертає статистику."""
        phones = {c.phone for c in self._contacts.values()}
        last = self._last_modified or "-"
        return {
            "contacts_count": len(self._contacts),
            "unique_phones_count": len(phones),
            "last_modified": last,
        }

    # -------------------------
    # Серіалізація для storage
    # -------------------------

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Перетворює книгу у dict для JSON."""
        data: Dict[str, Dict[str, str]] = {}
        for name, c in self._contacts.items():
            data[name] = {
                "name": c.name,
                "phone": c.phone,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, str]], *, allow_duplicate_phones: bool = False) -> "AddressBook":
        """Створює AddressBook з dict."""
        book = cls(allow_duplicate_phones=allow_duplicate_phones)
        for key, raw in data.items():
            # Мінімальна валідація при завантаженні: ім'я — ключ
            name = validate_name(raw.get("name", key))
            phone = normalize_phone(raw.get("phone", ""))
            created_at = raw.get("created_at") or _now_iso()
            updated_at = raw.get("updated_at") or created_at

            if name in book._contacts:
                # Якщо раптом є дубль імені — беремо перший, інше ігноруємо
                continue

            if not allow_duplicate_phones and book._has_phone(phone):
                # Дубль телефону при строгій політиці — ігноруємо
                continue

            book._contacts[name] = Contact(
                name=name,
                phone=phone,
                created_at=created_at,
                updated_at=updated_at,
            )

        book.is_dirty = False
        book._last_modified = None
        return book