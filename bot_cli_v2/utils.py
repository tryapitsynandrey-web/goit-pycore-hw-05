# utils.py
"""Утиліти для валідації і нормалізації.

Примітка:
- Нормалізація телефону робиться до міжнародного вигляду +XXXXXXXX...
- Це НЕ повноцінна бібліотека phone parsing, але достатньо для ДЗ/портфоліо-демо.
"""

from __future__ import annotations

import re


def validate_name(name: str) -> str:
    """Валідує і повертає очищене ім'я.

    Правила:
    - без пробілів на краях
    - мінімальна довжина 2
    """
    cleaned = name.strip()
    if len(cleaned) < 2:
        raise ValueError("Name too short")
    return cleaned


def normalize_phone(phone: str) -> str:
    """Нормалізує телефон до міжнародного формату.

    Правила:
    - дозволяємо '+' тільки на початку
    - прибираємо пробіли/дужки/дефіси та інші символи
    - дозволяємо 7..15 цифр (типовий діапазон E.164)
    - якщо номер починається з '00' -> замінюємо на '+'
    - якщо '+' немає, додаємо '+' (вважаємо, що користувач ввів міжнародний код без '+')
    """
    raw = phone.strip()
    if not raw:
        raise ValueError("Empty phone")

    # Якщо є плюс — він має бути тільки першим символом
    if raw.count("+") > 1 or ("+" in raw and not raw.startswith("+")):
        raise ValueError("Invalid '+' position")

    # Залишаємо цифри, а також один початковий +
    if raw.startswith("+"):
        digits = re.sub(r"\D", "", raw[1:])
        normalized = "+" + digits
    else:
        # 00XXXXXXXX -> +XXXXXXXX
        if raw.startswith("00"):
            digits = re.sub(r"\D", "", raw[2:])
            normalized = "+" + digits
        else:
            digits = re.sub(r"\D", "", raw)
            normalized = "+" + digits

    # Перевірка довжини (без '+')
    digits_only = normalized[1:]
    if not digits_only.isdigit():
        raise ValueError("Phone contains invalid characters")

    if not (7 <= len(digits_only) <= 15):
        raise ValueError("Phone length is invalid")

    return normalized