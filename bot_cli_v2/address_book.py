from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Contact:
    name: str
    phone: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Contact":
        name = str(data.get("name", "")).strip()
        phone = str(data.get("phone", "")).strip()

        created_at = str(data.get("created_at") or _now_iso())
        updated_at = str(data.get("updated_at") or created_at)

        return Contact(
            name=name,
            phone=phone,
            created_at=created_at,
            updated_at=updated_at,
        )


class AddressBook:
    """Мінімальний 'дорослий' AddressBook: add/change/remove/get/search/rename/stats."""

    def __init__(self, *, allow_duplicate_phones: bool = False) -> None:
        self._contacts: Dict[str, Contact] = {}
        self.allow_duplicate_phones = allow_duplicate_phones
        self.last_modified: str | None = None
        self.is_dirty: bool = False

    # -------------------------
    # internal helpers
    # -------------------------

    def _touch_modified(self) -> None:
        self.last_modified = _now_iso()
        self.is_dirty = True

    def _phone_in_use(self, phone: str, *, exclude_name: str | None = None) -> bool:
        for name, c in self._contacts.items():
            if exclude_name is not None and name == exclude_name:
                continue
            if c.phone == phone:
                return True
        return False

    # -------------------------
    # public API
    # -------------------------

    def load_from_dict(self, data: Dict[str, Any], *, last_modified: str | None = None) -> None:
        self._contacts.clear()
        for name, payload in data.items():
            if isinstance(payload, dict):
                c = Contact.from_dict(payload)
                # имя из ключа — приоритетнее (на случай старых форматов)
                c.name = str(name).strip() or c.name
                self._contacts[c.name] = c
            else:
                # старый формат: {"Bob": "+123..."}
                c = Contact(
                    name=str(name).strip(),
                    phone=str(payload).strip(),
                    created_at=_now_iso(),
                    updated_at=_now_iso(),
                )
                self._contacts[c.name] = c

        self.last_modified = last_modified
        self.is_dirty = False

    def to_dict(self) -> Dict[str, Any]:
        return {name: c.to_dict() for name, c in self._contacts.items()}

    def add(self, name: str, phone: str) -> None:
        name = str(name).strip()
        if not name:
            raise ValueError("Name is empty")

        if name in self._contacts:
            raise ValueError("Duplicate name")

        if (not self.allow_duplicate_phones) and self._phone_in_use(phone):
            raise ValueError("Duplicate phone")

        now = _now_iso()
        self._contacts[name] = Contact(name=name, phone=phone, created_at=now, updated_at=now)
        self._touch_modified()

    def change(self, name: str, phone: str) -> None:
        name = str(name).strip()
        if name not in self._contacts:
            raise KeyError(name)

        if (not self.allow_duplicate_phones) and self._phone_in_use(phone, exclude_name=name):
            raise ValueError("Duplicate phone")

        c = self._contacts[name]
        c.phone = phone
        c.updated_at = _now_iso()
        self._touch_modified()

    def remove(self, name: str) -> None:
        name = str(name).strip()
        if name not in self._contacts:
            raise KeyError(name)

        del self._contacts[name]
        self._touch_modified()

    def rename(self, old_name: str, new_name: str) -> None:
        old_name = str(old_name).strip()
        new_name = str(new_name).strip()

        if not new_name:
            raise ValueError("Name is empty")

        if old_name not in self._contacts:
            raise KeyError(old_name)

        if new_name in self._contacts:
            raise ValueError("Duplicate name")

        c = self._contacts.pop(old_name)
        c.name = new_name
        c.updated_at = _now_iso()
        self._contacts[new_name] = c
        self._touch_modified()

    def get_record(self, name: str) -> Dict[str, Any]:
        name = str(name).strip()
        if name not in self._contacts:
            raise KeyError(name)
        return self._contacts[name].to_dict()

    def get_phone(self, name: str) -> str:
        return self.get_record(name)["phone"]

    def all_records(self) -> List[Dict[str, Any]]:
        return [self._contacts[name].to_dict() for name in sorted(self._contacts)]

    def search(self, query: str) -> List[Tuple[str, str]]:
        q = str(query).strip().casefold()
        if not q:
            raise ValueError("Query is empty")

        results: List[Tuple[str, str]] = []
        for name, c in self._contacts.items():
            if (q in name.casefold()) or (q in c.phone.casefold()):
                results.append((name, c.phone))

        results.sort(key=lambda x: x[0].casefold())
        return results

    def stats(self) -> Dict[str, Any]:
        phones = [c.phone for c in self._contacts.values()]
        return {
            "total_contacts": len(self._contacts),
            "unique_phones": len(set(phones)),
            "last_modified": self.last_modified,
            "allow_duplicate_phones": self.allow_duplicate_phones,
        }