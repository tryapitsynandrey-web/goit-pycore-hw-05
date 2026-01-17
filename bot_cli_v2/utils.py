from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


# =========================
# НОРМАЛІЗАЦІЯ ТЕЛЕФОНУ
# =========================

def normalize_phone(raw_phone: str) -> str:
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
        phone = "+" + digits

    if not digits.isdigit():
        raise ValueError("Phone must contain digits only")

    # Мін/макс довжина за E.164 (до 15 цифр після '+')
    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone length must be between 7 and 15 digits")

    return phone


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
    """Завжди рендерить контакти як ASCII-таблицю (стабільний вивід)."""
    rows: List[Tuple[str, str, str, str]] = []

    for r in records:
        name = str(r.get("name", "")).strip()
        phone = str(r.get("phone", "")).strip()
        created = _fmt_dt(r.get("created_at"))
        updated = _fmt_dt(r.get("updated_at"))
        rows.append((name, phone, created, updated))

    if not rows:
        return ""

    headers = ("Name", "Phone", "Created", "Updated")

    w_name = max(len(headers[0]), *(len(x[0]) for x in rows))
    w_phone = max(len(headers[1]), *(len(x[1]) for x in rows))
    w_created = max(len(headers[2]), *(len(x[2]) for x in rows))
    w_updated = max(len(headers[3]), *(len(x[3]) for x in rows))

    def sep() -> str:
        return (
            "+"
            + "-" * (w_name + 2)
            + "+"
            + "-" * (w_phone + 2)
            + "+"
            + "-" * (w_created + 2)
            + "+"
            + "-" * (w_updated + 2)
            + "+"
        )

    header_line = (
        f"| {headers[0]:<{w_name}} | {headers[1]:<{w_phone}} | "
        f"{headers[2]:<{w_created}} | {headers[3]:<{w_updated}} |"
    )

    body_lines = [
        f"| {name:<{w_name}} | {phone:<{w_phone}} | {created:<{w_created}} | {updated:<{w_updated}} |"
        for name, phone, created, updated in rows
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
        out.append(f"| {k:<{w_key}} : {str(v):<{inner_w - (w_key + 3)}} |")
    out.append(top)
    return "\n".join(out)