from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from address_book import AddressBook
from settings import SETTINGS
from storage import load_contacts_json, save_contacts_json
from utils import normalize_phone

logger = logging.getLogger("assistant_bot")


class AppService:
    """Тонкий шар сервісу поверх AddressBook + збереження для повторного використання в CLI та HTTP API."""

    def __init__(
        self,
        data_dir: Path,
        enable_backups: bool = True,
        allow_duplicate_phones: bool = False,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.json_path = self.data_dir / "contacts.json"
        contacts, last_modified = load_contacts_json(self.json_path)
        self.book = AddressBook(contacts, allow_duplicate_phones=allow_duplicate_phones)
        if last_modified:
            self.book.last_modified = last_modified
        self.enable_backups = enable_backups
        # Стеки undo/redo зберігають зворотні операції для відновлення попереднього стану
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []

    def all(self) -> List[Dict[str, Any]]:
        return self.book.all_records_sorted()

    def get(self, name: str) -> Dict[str, Any]:
        return self.book.get_record(name)

    def add(
        self,
        name: str,
        phone: str,
        birthday: str | None = None,
        notes: str | None = None,
    ) -> None:
        self.book.add(name, phone, birthday=birthday, notes=notes)
        # зворотна операція для undo — видалення
        self._undo_stack.append({"op": "remove", "name": name})
        self._redo_stack.clear()
        self._save()

    def change(
        self,
        name: str,
        phone: str,
        birthday: str | None = None,
        notes: str | None = None,
    ) -> None:
        # зберегти старий номер для undo
        old = self.book.get(name)
        # зберегти старі birthday/notes для redo
        old_rec = self.book.get_record(name)
        self.book.change(name, phone, birthday=birthday, notes=notes)
        self._undo_stack.append(
            {
                "op": "change",
                "name": name,
                "phone": old,
                "birthday": old_rec.get("birthday"),
                "notes": old_rec.get("notes"),
            }
        )
        self._redo_stack.clear()
        self._save()

    def remove(self, name: str) -> None:
        # зберегти запис для undo
        rec = self.book.get_record(name)
        self.book.remove(name)
        self._undo_stack.append({"op": "add_record", "record": rec})
        self._redo_stack.clear()
        self._save()

    def rename(self, old: str, new: str) -> None:
        self.book.rename(old, new)
        # зворотна операція — перейменувати назад
        self._undo_stack.append({"op": "rename", "old": new, "new": old})
        self._redo_stack.clear()
        self._save()

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.book.search(query)

    def stats(self) -> Dict[str, Any]:
        return self.book.stats()

    def upcoming_birthdays(self, days: int = 7) -> List[Dict[str, Any]]:
        """Повертає список контактів з днем народження у наступні `days` днів.

        Кожен повернений словник міститиме додатковий ключ `days_until`.
        """
        from datetime import date, datetime

        out: List[Dict[str, Any]] = []
        today = date.today()

        for rec in self.book.all_records_sorted():
            b = rec.get("birthday")
            if not b:
                continue
            try:
                # Очікуємо формат YYYY-MM-DD
                dt = datetime.strptime(str(b), "%Y-%m-%d").date()
            except Exception:
                continue

            # наступне настання у цьому році
            this_year = dt.replace(year=today.year)
            if this_year < today:
                next_occurrence = this_year.replace(year=today.year + 1)
            else:
                next_occurrence = this_year

            delta = (next_occurrence - today).days
            if 0 <= delta <= days:
                copy = dict(rec)
                copy["days_until"] = delta
                out.append(copy)

        out.sort(key=lambda r: r.get("days_until", 0))
        return out

    def _save(self) -> None:
        try:
            save_contacts_json(
                self.json_path,
                self.book.to_dict(),
                self.book.last_modified,
                enable_backups=self.enable_backups,
            )
        except Exception:
            logger.exception("Failed to save contacts to %s", self.json_path)

    def import_csv(self, csv_path: Path) -> Dict[str, int]:
        """Імпортує контакти з CSV як одну транзакційну операцію.

        Додаються лише нові контакти (дублікати пропускаються). Увесь імпорт
        фіксується як одна відкотна операція, яка видалить усі
        контакти, додані цим імпортом.
        """
        added_names: List[str] = []
        skipped = 0
        try:
            with csv_path.open("r", encoding="utf-8", newline="") as fh:
                import csv as _csv

                reader = _csv.DictReader(fh)
                for row in reader:
                    name = str(row.get("name", "")).strip()
                    phone = str(row.get("phone", "")).strip()
                    birthday = str(row.get("birthday", "")).strip() or None
                    notes = str(row.get("notes", "")).strip() or None
                    if not name or not phone:
                        skipped += 1
                        continue
                    try:
                        # нормалізувати телефон перед додаванням
                        normalized = normalize_phone(
                            phone, default_country_code=SETTINGS.default_country_code
                        )
                        self.book.add(name, normalized, birthday=birthday, notes=notes)
                        added_names.append(name)
                    except Exception:
                        skipped += 1
        except FileNotFoundError:
            raise

        # Записати одну масову undo-операцію для всіх доданих імен
        if added_names:
            self._undo_stack.append({"op": "bulk_add", "names": added_names})
            self._redo_stack.clear()
            self._save()

        return {"added": len(added_names), "skipped": skipped}

    def undo(self) -> None:
        """Відмінити останню операцію."""
        if not self._undo_stack:
            raise RuntimeError("Nothing to undo")

        op = self._undo_stack.pop()
        # Виконати зворотну операцію і додати протилежну до стека redo
        if op["op"] == "remove":
            name = op["name"]
            # виконати видалення
            self.book.remove(name)
            self._redo_stack.append({"op": "add", "name": name, "phone": None})
        elif op["op"] == "add_record":
            rec = op["record"]
            self.book.add(rec.get("name"), rec.get("phone"))
            self._redo_stack.append({"op": "remove", "name": rec.get("name")})
        elif op["op"] == "change":
            name = op["name"]
            phone = op["phone"]
            # отримати поточний для redo
            current = self.book.get(name)
            self.book.change(name, phone)
            self._redo_stack.append({"op": "change", "name": name, "phone": current})
        elif op["op"] == "rename":
            old = op["old"]
            new = op["new"]
            self.book.rename(old, new)
            self._redo_stack.append({"op": "rename", "old": new, "new": old})
        elif op["op"] == "bulk_add":
            # Відміна bulk_add: видалити всі імена, що були додані
            names = op.get("names", []) or []
            # зберегти видалені записи в redo як add_record записи
            removed_records = []
            for name in names:
                rec = self.book.get_record(name)
                if rec:
                    removed_records.append(rec)
                    try:
                        self.book.remove(name)
                    except Exception:
                        # якщо не вдається видалити — пропустити
                        pass
            self._redo_stack.append({"op": "bulk_remove", "records": removed_records})
        else:
            raise RuntimeError("Unknown undo operation")

        self._save()

    def redo(self) -> None:
        """Повторити останню відправлену назад операцію (redo)."""
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo")

        op = self._redo_stack.pop()
        # Повторно застосувати операцію, додавши зворотну в стек undo
        if op["op"] == "add":
            name = op["name"]
            phone = op.get("phone") or ""
            self.book.add(name, phone)
            self._undo_stack.append({"op": "remove", "name": name})
        elif op["op"] == "remove":
            name = op["name"]
            rec = self.book.get_record(name)
            self.book.remove(name)
            self._undo_stack.append({"op": "add_record", "record": rec})
        elif op["op"] == "change":
            name = op["name"]
            phone = op["phone"]
            old = self.book.get(name)
            self.book.change(name, phone)
            self._undo_stack.append({"op": "change", "name": name, "phone": old})
        elif op["op"] == "rename":
            old = op["old"]
            new = op["new"]
            self.book.rename(old, new)
            self._undo_stack.append({"op": "rename", "old": new, "new": old})
        elif op["op"] == "bulk_remove":
            # Redoing a bulk remove: re-add preserved records
            records = op.get("records", []) or []
            for rec in records:
                try:
                    self.book.add(rec.get("name"), rec.get("phone"))
                    # inverse for undo is remove of that name
                    self._undo_stack.append({"op": "remove", "name": rec.get("name")})
                except Exception:
                    # ignore individual failures
                    pass
        else:
            raise RuntimeError("Unknown redo operation")

        self._save()
