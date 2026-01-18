from __future__ import annotations

import glob
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_contacts_json(path: Path) -> Tuple[Dict[str, Any], str | None]:
    """Завантажити JSON контактів і привести до формату mapping name->record-dict.

    Підтримуються застарілі формати, де значення — рядок з телефоном,
    і новий формат, де значення — повний словник запису. Повертає (contacts, last_modified).
    """
    if not path.exists():
        return {}, None

    data = json.loads(path.read_text(encoding="utf-8"))

    last_modified = None
    # Якщо payload обгорнуто у структуру з полем contacts і meta
    if (
        isinstance(data, dict)
        and "contacts" in data
        and isinstance(data["contacts"], dict)
    ):
        raw_contacts = data["contacts"]
        meta = data.get("meta")
        if isinstance(meta, dict):
            lm = meta.get("last_modified")
            if isinstance(lm, str):
                last_modified = lm
    elif isinstance(data, dict):
        raw_contacts = data
    else:
        return {}, None

    contacts: Dict[str, Any] = {}
    for k, v in raw_contacts.items():
        name = str(k)
        # Якщо значення вже є словником (record), зберігаємо як є
        if isinstance(v, dict):
            contacts[name] = v
            continue

        # Застарілий формат: значення — рядок з телефоном
        phone = str(v)
        created = _now_iso()
        contacts[name] = {
            "name": name,
            "phone": phone,
            "created_at": created,
            "updated_at": created,
        }

    return contacts, last_modified


def save_contacts_json(
    path: Path,
    contacts: Dict[str, Any],
    last_modified: str | None,
    enable_backups: bool = True,
) -> None:
    """Зберегти контакти. Підтримує mapping name->record-dict або name->phone-string (застарілий).

    Нормалізує просту застарілу структуру до формату record перед збереженням.
    """
    normalized: Dict[str, Any] = {}
    for name, rec in contacts.items():
        if isinstance(rec, dict):
            normalized[name] = rec
        else:
            normalized[name] = {
                "name": str(name),
                "phone": str(rec),
                "created_at": None,
                "updated_at": None,
            }

    payload = {"contacts": normalized, "meta": {"last_modified": last_modified}}

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Якщо цільовий файл існує — створити timestamped backup перед заміною та очистити старі бекапи
    if path.exists() and enable_backups:
        _create_backup(path)

    tmp_path.replace(path)


def _create_backup(path: Path, max_backups: int = 5) -> None:
    """Create a timestamped backup for `path` and keep up to `max_backups` backups."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup_name = f"{path.name}.backup.{ts}"
    backup_path = path.parent / backup_name
    shutil.copy2(path, backup_path)

    # Очищення старих резервних копій
    pattern = str(path.parent / f"{path.name}.backup.*")
    files: List[str] = sorted(
        glob.glob(pattern), key=lambda p: Path(p).stat().st_mtime, reverse=True
    )
    for old in files[max_backups:]:
        try:
            Path(old).unlink()
        except Exception:
            pass


def load_contacts_txt(path: Path) -> Dict[str, str]:
    """Старий формат: name: phone або name,phone (підтримуємо обидва)."""
    contacts: Dict[str, str] = {}
    if not path.exists():
        return contacts

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if ":" in line:
            name, phone = [p.strip() for p in line.split(":", 1)]
        elif "," in line:
            name, phone = [p.strip() for p in line.split(",", 1)]
        else:
            continue

        if name and phone:
            contacts[name] = phone

    return contacts


def migrate_txt_to_json_if_needed(base_dir: Path, enable_backups: bool = True) -> None:
    txt_path = base_dir / "contacts.txt"
    json_path = base_dir / "contacts.json"

    if json_path.exists():
        return

    if not txt_path.exists():
        return

    contacts = load_contacts_txt(txt_path)
    # створити резервну копію TXT-джерела перед міграцією
    try:
        if enable_backups:
            _create_backup(txt_path, max_backups=3)
    except Exception:
        pass

    save_contacts_json(
        json_path, contacts, last_modified=None, enable_backups=enable_backups
    )
