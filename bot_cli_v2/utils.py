from __future__ import annotations

import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Tuple

try:
    from rapidfuzz import fuzz as _rf_fuzz
    from rapidfuzz import process as _rf_process

    _RF_AVAILABLE = True
except Exception:
    _RF_AVAILABLE = False
from datetime import datetime as _dt

from exceptions import ValidationError


def validate_birthday(value: str | None) -> str | None:
    """Перевіряє день народження у форматі YYYY-MM-DD. Повертає рядок або None.

    Викликає ValidationError при невірному форматі.
    """
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return None
    try:
        _dt.strptime(v, "%Y-%m-%d")
        return v
    except Exception:
        raise ValidationError("Invalid birthday format, expected YYYY-MM-DD")


# =========================
# НОРМАЛІЗАЦІЯ ТЕЛЕФОНУ
# =========================


def normalize_phone(raw_phone: str, default_country_code: str | None = None) -> str:
    """Нормалізує телефон до єдиного канонічного формату.

    Правила:
    - прибираємо пробіли/дужки/дефіси/тощо
    - дозволяємо '+' лише на початку
    - '00XXXXXXXX' -> '+XXXXXXXX'
    - результат: '+' + лише цифри
    - перевірка довжини: 7..15 цифр (E.164)
    """
    phone = raw_phone.strip()
    if not phone:
        raise ValueError("Phone is empty")

    # Залишаємо тільки цифри та '+'
    phone = re.sub(r"[^\d+]", "", phone)

    # Якщо '+' зустрічається не на початку — це помилка
    if "+" in phone[1:]:
        raise ValueError("Plus sign must be at the beginning")

    # 00XXXXXXXX -> +XXXXXXXX
    if phone.startswith("00"):
        phone = "+" + phone[2:]

    if phone.startswith("+"):
        digits = phone[1:]
    else:
        digits = phone
        # Якщо локальний формат (починається з '0') і вказано код країни,
        # перетворити в міжнародний формат, видаливши провідний нуль і додавши код країни
        if default_country_code and digits.startswith("0"):
            cc = default_country_code.lstrip("+")
            digits = cc + digits.lstrip("0")
        phone = "+" + digits

    if not digits.isdigit():
        raise ValueError("Phone must contain digits only")

    # Мін/макс довжина за E.164 (до 15 цифр після '+')
    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone length must be between 7 and 15 digits")

    return phone


def validate_name(name: str) -> str:
    """Strip and validate a contact name. Raises ValueError on invalid input."""
    n = str(name).strip()
    if not n:
        raise ValidationError("Name is empty")
    if len(n) < 2:
        raise ValidationError("Name too short")
    return n


# =========================
# ФОРМАТУВАННЯ ВИВОДУ
# =========================


def _fmt_dt(value: Any) -> str:
    """Форматує ISO-дату в 'YYYY-MM-DD HH:MM'."""
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def format_contacts_table(records: Iterable[Dict[str, Any]]) -> str:
    """Відформатовує контакти у вигляді ASCII-таблиці з полями birthday та notes."""
    rows: List[Tuple[str, str, str, str, str, str]] = []

    for r in records:
        name = str(r.get("name", "")).strip()
        phone = str(r.get("phone", "")).strip()
        birthday = str(r.get("birthday", "") or "").strip()
        notes = str(r.get("notes", "") or "").strip()
        if len(notes) > 30:
            notes_disp = notes[:27] + "..."
        else:
            notes_disp = notes
        created = _fmt_dt(r.get("created_at"))
        updated = _fmt_dt(r.get("updated_at"))
        rows.append((name, phone, birthday, notes_disp, created, updated))

    if not rows:
        return ""

    headers = ("Name", "Phone", "Birthday", "Notes", "Created", "Updated")

    w_name = max(len(headers[0]), *(len(x[0]) for x in rows))
    w_phone = max(len(headers[1]), *(len(x[1]) for x in rows))
    w_bday = max(len(headers[2]), *(len(x[2]) for x in rows))
    w_notes = max(len(headers[3]), *(len(x[3]) for x in rows))
    w_created = max(len(headers[4]), *(len(x[4]) for x in rows))
    w_updated = max(len(headers[5]), *(len(x[5]) for x in rows))

    def sep() -> str:
        return (
            "+"
            + "-" * (w_name + 2)
            + "+"
            + "-" * (w_phone + 2)
            + "+"
            + "-" * (w_bday + 2)
            + "+"
            + "-" * (w_notes + 2)
            + "+"
            + "-" * (w_created + 2)
            + "+"
            + "-" * (w_updated + 2)
            + "+"
        )

    header_line = (
        f"| {headers[0]:<{w_name}} | {headers[1]:<{w_phone}} | {headers[2]:<{w_bday}} | {headers[3]:<{w_notes}} | "
        f"{headers[4]:<{w_created}} | {headers[5]:<{w_updated}} |"
    )

    body_lines = [
        f"| {name:<{w_name}} | {phone:<{w_phone}} | {bday:<{w_bday}} | {notes:<{w_notes}} | {created:<{w_created}} | {updated:<{w_updated}} |"
        for name, phone, bday, notes, created, updated in rows
    ]

    return "\n".join([sep(), header_line, sep(), *body_lines, sep()])


def format_stats_box(stats: Dict[str, Any]) -> str:
    """Рендерить статистику як ASCII-бокс (читабельний вивід)."""
    lines = [
        ("total_contacts", stats.get("total_contacts", 0)),
        ("unique_phones", stats.get("unique_phones", 0)),
        ("last_modified", _fmt_dt(stats.get("last_modified"))),
        ("allow_duplicate_phones", stats.get("allow_duplicate_phones", False)),
    ]

    title = "AddressBook stats"
    w_key = max(len(k) for k, _ in lines)
    w_val = max(len(str(v)) for _, v in lines)
    inner_w = max(len(title), w_key + 3 + w_val)

    top = "+" + "-" * (inner_w + 2) + "+"
    mid = "+" + "-" * (inner_w + 2) + "+"

    out = [top, f"| {title:<{inner_w}} |", mid]
    for k, v in lines:
        out.append(f"| {k:<{w_key}} : {v!s:<{inner_w - (w_key + 3)}} |")
    out.append(top)
    return "\n".join(out)


def fuzzy_search(
    query: str,
    records: Iterable[Dict[str, Any]],
    key_fields: List[str] | None = None,
    limit: int = 10,
    score_cutoff: int = 60,
) -> List[Dict[str, Any]]:
    """Нечіткий пошук по записах з комбінуванням вказаних `key_fields`.

    Використовує rapidfuzz, якщо доступний, інакше повертає на основі difflib.
    Повертає список співпадінь, відсортований за спаданням оцінки.
    """
    q = (query or "").strip()
    if not q:
        return []

    key_fields = key_fields or ["name", "phone"]

    choices = []
    mapping = {}
    for idx, r in enumerate(records):
        parts = []
        for k in key_fields:
            parts.append(str(r.get(k, "")).strip())
        choice = " | ".join(p for p in parts if p)
        key = f"{idx}:{choice}"
        choices.append(choice)
        mapping[choice] = dict(r)

    results: List[Tuple[float, Dict[str, Any]]] = []

    if _RF_AVAILABLE:
        # rapidfuzz повертає (choice, score, idx)
        extracted = _rf_process.extract(q, choices, scorer=_rf_fuzz.WRatio, limit=limit)
        for choice, score, _ in extracted:
            if score >= score_cutoff:
                results.append((score, mapping[choice]))
    else:
        # запасний варіант із використанням difflib.SequenceMatcher
        for choice in choices:
            ratio = int(SequenceMatcher(None, q.lower(), choice.lower()).ratio() * 100)
            if ratio >= score_cutoff:
                results.append((ratio, mapping[choice]))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in results[:limit]]
