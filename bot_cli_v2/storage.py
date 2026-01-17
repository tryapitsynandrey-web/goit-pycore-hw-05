from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple


def load_contacts_json(path: Path) -> Tuple[Dict[str, str], str | None]:
    if not path.exists():
        return {}, None

    data = json.loads(path.read_text(encoding="utf-8"))

    # Поддерживаем два формата:
    # 1) просто dict контактов
    # 2) {"contacts": {...}, "meta": {"last_modified": "..."}}
    if isinstance(data, dict) and "contacts" in data and isinstance(data["contacts"], dict):
        contacts = {str(k): str(v) for k, v in data["contacts"].items()}
        last_modified = None
        meta = data.get("meta")
        if isinstance(meta, dict):
            lm = meta.get("last_modified")
            if isinstance(lm, str):
                last_modified = lm
        return contacts, last_modified

    if isinstance(data, dict):
        contacts = {str(k): str(v) for k, v in data.items()}
        return contacts, None

    return {}, None


def save_contacts_json(path: Path, contacts: Dict[str, str], last_modified: str | None) -> None:
    payload = {
        "contacts": contacts,
        "meta": {
            "last_modified": last_modified,
        },
    }

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


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


def migrate_txt_to_json_if_needed(base_dir: Path) -> None:
    txt_path = base_dir / "contacts.txt"
    json_path = base_dir / "contacts.json"

    if json_path.exists():
        return

    if not txt_path.exists():
        return

    contacts = load_contacts_txt(txt_path)
    save_contacts_json(json_path, contacts, last_modified=None)