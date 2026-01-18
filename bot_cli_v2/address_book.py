from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from exceptions import (
    ContactNotFoundError,
    DuplicateNameError,
    DuplicatePhoneError,
)
from utils import validate_name


def _now_iso() -> str:
    """Повертає поточний час в ISO форматі (UTC)."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Contact:
    """Структура контакту (опційно корисна для типізації)."""

    name: str
    phone: str
    created_at: str
    updated_at: str
    birthday: Optional[str] = None
    notes: Optional[str] = None


class AddressBook:
    """Мінімальний AddressBook.

    Формат зберігання:
        {
          "Bill": {"name": "Bill", "phone": "+123...", "created_at": "...", "updated_at": "..."}
        }
    """

    def __init__(
        self,
        data: Dict[str, Dict[str, Any]] | None = None,
        allow_duplicate_phones: bool = False,
    ) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}
        self.allow_duplicate_phones = allow_duplicate_phones
        self.last_modified: str | None = None
        if data:
            # завантажити початковий словник даних, якщо він наданий
            self.load_from_dict(data)

    # ---------- завантаження / збереження ----------

    def load_from_dict(
        self, data: Dict[str, Dict[str, Any]], last_modified: str | None = None
    ) -> None:
        """Завантажує дані зі словника (наприклад, з JSON)."""
        self._data = {}

        for name, rec in (data or {}).items():
            if not isinstance(rec, dict):
                continue

            n = str(rec.get("name") or name).strip()
            p = str(rec.get("phone") or "").strip()
            created = str(rec.get("created_at") or _now_iso())
            updated = str(rec.get("updated_at") or created)
            birthday = rec.get("birthday")
            notes = rec.get("notes")

            self._data[n] = {
                "name": n,
                "phone": p,
                "created_at": created,
                "updated_at": updated,
                "birthday": birthday,
                "notes": notes,
            }

        # Якщо є записи — ставимо last_modified, інакше None
        self.last_modified = last_modified or (_now_iso() if self._data else None)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Повертає копію внутрішніх даних для збереження."""
        return {name: dict(rec) for name, rec in self._data.items()}

    # ---------- допоміжні функції ----------

    def _touch(self) -> None:
        """Оновлює last_modified після будь-яких змін."""
        self.last_modified = _now_iso()

    def _validate_name(self, name: str) -> str:
        """Валідація імені контакту."""
        return validate_name(name)

    def _ensure_unique_phone(self, phone: str, ignore_name: str | None = None) -> None:
        """Перевіряє унікальність телефону (якщо політика забороняє дублікати)."""
        if self.allow_duplicate_phones:
            return

        for name, rec in self._data.items():
            if ignore_name is not None and name == ignore_name:
                continue
            if rec.get("phone") == phone:
                raise DuplicatePhoneError("Duplicate phone")

    # ---------- команди / операції ----------

    def add(
        self,
        name: str,
        phone: str,
        birthday: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Додає новий контакт."""
        n = self._validate_name(name)

        if n in self._data:
            raise DuplicateNameError("Duplicate name")

        self._ensure_unique_phone(phone)

        now = _now_iso()
        self._data[n] = {
            "name": n,
            "phone": phone,
            "created_at": now,
            "updated_at": now,
            "birthday": birthday,
            "notes": notes,
        }
        self._touch()

    def change(
        self,
        name: str,
        phone: str,
        birthday: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Змінює телефон існуючого контакту."""
        n = self._validate_name(name)

        if n not in self._data:
            raise ContactNotFoundError(n)

        self._ensure_unique_phone(phone, ignore_name=n)

        self._data[n]["phone"] = phone
        if birthday is not None:
            self._data[n]["birthday"] = birthday
        if notes is not None:
            self._data[n]["notes"] = notes
        self._data[n]["updated_at"] = _now_iso()
        self._touch()

    def remove(self, name: str) -> None:
        """Видаляє контакт."""
        n = self._validate_name(name)

        if n not in self._data:
            raise ContactNotFoundError(n)

        del self._data[n]
        self._touch()

    def rename(self, old_name: str, new_name: str) -> None:
        """Перейменовує контакт без зміни телефону."""
        old_n = self._validate_name(old_name)
        new_n = self._validate_name(new_name)

        if old_n not in self._data:
            raise ContactNotFoundError(old_n)

        if new_n in self._data:
            raise DuplicateNameError("Duplicate name")

        rec = self._data.pop(old_n)
        rec["name"] = new_n
        rec["updated_at"] = _now_iso()
        self._data[new_n] = rec
        self._touch()

    def get_record(self, name: str) -> Dict[str, Any]:
        """Повертає запис контакту (dict)."""
        n = self._validate_name(name)

        if n not in self._data:
            raise ContactNotFoundError(n)

        return dict(self._data[n])

    def get(self, name: str) -> str:
        """Повертає телефон контакту (сумісність зі старим API)."""
        return self.get_record(name)["phone"]

    def all_records_sorted(self) -> List[Dict[str, Any]]:
        """Повертає всі записи контактів, відсортовані за ім'ям."""
        return [dict(self._data[name]) for name in sorted(self._data)]

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Пошук за частковим збігом по імені або телефону."""
        q = (query or "").strip()
        if not q:
            raise ValueError("Empty query")

        q_low = q.casefold()
        out: List[Dict[str, Any]] = []

        for name, rec in self._data.items():
            phone = str(rec.get("phone", ""))
            if q_low in name.casefold() or q_low in phone:
                out.append(dict(rec))

        # Відсортуємо результати за ім'ям для стабільного виводу
        out.sort(key=lambda r: str(r.get("name", "")).casefold())
        return out

    def stats(self) -> Dict[str, Any]:
        """Повертає статистику адресної книги."""
        phones = [str(rec.get("phone", "")) for rec in self._data.values()]
        unique_phones = len(set(phones))

        return {
            "total_contacts": len(self._data),
            "unique_phones": unique_phones,
            "last_modified": self.last_modified,
            "allow_duplicate_phones": self.allow_duplicate_phones,
        }
