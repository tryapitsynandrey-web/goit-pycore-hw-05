from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple


# =========================
# PHONE NORMALIZATION
# =========================

def normalize_phone(raw_phone: str) -> str:
    """Нормалізує телефон до єдиного формату (+XXXXXXXX)."""

    phone = raw_phone.strip()
    if not phone:
        raise ValueError("Phone is empty")

    phone = re.sub(r"[^\d+]", "", phone)

    if "+" in phone[1:]:
        raise ValueError("Plus sign must be at the beginning")

    if phone.startswith("00"):
        phone = "+" + phone[2:]

    if phone.startswith("+"):
        digits = phone[1:]
    else:
        digits = phone
        phone = "+" + digits

    if not digits.isdigit():
        raise ValueError("Phone must contain digits only")

    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone length must be between 7 and 15 digits")

    return phone


# =========================
# FORMATTING HELPERS
# =========================

def _fmt_dt(value: Any) -> str:
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def format_contacts_table(records: Iterable[Dict[str, Any]]) -> str:
    """Формує красиву ASCII-таблицю контактів."""

    rows: List[Tuple[str, str, str, str]] = []

    for r in records:
        if not isinstance(r, dict):
            continue
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

    def hline(left: str, mid: str, right: str) -> str:
        return (
            left
            + "─" * (w_name + 2) + mid
            + "─" * (w_phone + 2) + mid
            + "─" * (w_created + 2) + mid
            + "─" * (w_updated + 2)
            + right
        )

    top = hline("┌", "┬", "┐")
    sep = hline("├", "┼", "┤")
    bottom = hline("└", "┴", "┘")

    header_row = (
        f"│ {headers[0]:<{w_name}} │ {headers[1]:<{w_phone}} │ "
        f"{headers[2]:<{w_created}} │ {headers[3]:<{w_updated}} │"
    )

    body_rows = [
        f"│ {n:<{w_name}} │ {p:<{w_phone}} │ {c:<{w_created}} │ {u:<{w_updated}} │"
        for n, p, c, u in rows
    ]

    return "\n".join([top, header_row, sep, *body_rows, bottom])


def format_stats_box(stats: Dict[str, Any]) -> str:
    """Формує красивий блок статистики."""

    lines = [
        ("total_contacts", stats.get("total_contacts", 0)),
        ("unique_phones", stats.get("unique_phones", 0)),
        ("last_modified", _fmt_dt(stats.get("last_modified"))),
        ("allow_duplicate_phones", stats.get("allow_duplicate_phones", False)),
    ]

    title = "📊 AddressBook stats"
    w_key = max(len(k) for k, _ in lines)
    w_val = max(len(str(v)) for _, v in lines)
    width = max(len(title), w_key + w_val + 5)

    top = "┌" + "─" * (width + 2) + "┐"
    mid = "├" + "─" * (width + 2) + "┤"
    bot = "└" + "─" * (width + 2) + "┘"

    out = [top, f"│ {title:<{width}} │", mid]
    for k, v in lines:
        out.append(f"│ {k:<{w_key}} : {str(v):<{width - (w_key + 3)}} │")
    out.append(bot)
    return "\n".join(out)