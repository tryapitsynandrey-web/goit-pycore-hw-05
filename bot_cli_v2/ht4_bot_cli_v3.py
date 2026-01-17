# main.py
"""Консольний асистент-бот.

Функціонал:
- hello, help
- add <name> <phone>
- change <name> <phone>
- phone <name>
- all
- search <query>
- rename <old_name> <new_name>
- remove <name> / delete <name> (із підтвердженням)
- stats
- close / exit

Особливості:
- UX-повідомлення винесені в ux_messages.py
- Дані зберігаються у contacts.json (автоматично), з міграцією з contacts.txt
- Обробка помилок введення через декоратор input_error (IndexError, ValueError, KeyError)
- Телефони нормалізуються до міжнародного формату +XXXXXXXX...
- Логування у logfile.log
"""

from __future__ import annotations

import logging
import random
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

from address_book import AddressBook
from storage import load_address_book, save_address_book
from ux_messages import (
    ALLOW_DUPLICATE_PHONES,
    AUTO_HELP_EVERY_EMPTY_INPUTS,
    CONFIRM_REMOVE_MESSAGES,
    CONTACT_ADDED_MESSAGES,
    CONTACT_UPDATED_MESSAGES,
    ENTER_COMMAND_ARGUMENTS_MESSAGES,
    ENTER_NAME_AND_PHONE_MESSAGES,
    ENTER_NAME_MESSAGES,
    GOODBYE_MESSAGES,
    HELP_MESSAGE,
    INVALID_COMMAND_MESSAGES,
    NO_CONTACTS_MESSAGES,
    OPERATION_CANCELLED_MESSAGES,
    REMOVE_SUCCESS_MESSAGES,
    RENAME_SUCCESS_MESSAGES,
    SEARCH_NO_RESULTS_MESSAGES,
    STATS_HEADER_MESSAGES,
    WELCOME_MESSAGES,
)

LOG_FILENAME = "logfile.log"


# =========================
# ДОПОМІЖНІ ФУНКЦІЇ
# =========================

def setup_logging(base_dir: Path) -> None:
    """Налаштовує логування у файл logfile.log."""
    log_path = base_dir / LOG_FILENAME
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def pick_message(messages: Sequence[str]) -> str:
    """Повертає випадкове повідомлення з набору."""
    return random.choice(messages)


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Розбиває введення користувача на команду та аргументи."""
    cleaned = user_input.strip()
    if not cleaned:
        return "", []
    parts = cleaned.split()
    return parts[0].lower(), parts[1:]


# =========================
# ДЕКОРАТОР ДЛЯ ПОМИЛОК ВВОДУ
# =========================

def input_error(
    *,
    index_error_messages: Sequence[str] | None = None,
    key_error_messages: Sequence[str] | None = None,
    value_error_messages: Sequence[str] | None = None,
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Декоратор для обробки помилок введення користувача.

    Обробляє:
    - IndexError: немає аргументів
    - ValueError: некоректні аргументи / валідація
    - KeyError: контакт не знайдено
    """
    index_msgs = index_error_messages or ENTER_COMMAND_ARGUMENTS_MESSAGES
    key_msgs = key_error_messages or ("Contact not found. 🙁📇",)
    value_msgs = value_error_messages or ENTER_COMMAND_ARGUMENTS_MESSAGES

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> str:
            try:
                return func(*args, **kwargs)
            except IndexError:
                return pick_message(index_msgs)
            except KeyError:
                return pick_message(key_msgs)
            except ValueError:
                return pick_message(value_msgs)

        return inner

    return decorator


# =========================
# HANDLERS КОМАНД
# =========================

@input_error()
def say_hello(_args: List[str], _book: AddressBook) -> str:
    """Команда привітання."""
    return "How can I help you? 🙂👋"


@input_error()
def show_help(_args: List[str], _book: AddressBook) -> str:
    """Показує довідку."""
    return HELP_MESSAGE


@input_error(value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES)
def add_contact(args: List[str], book: AddressBook) -> str:
    """Додає новий контакт."""
    name, phone = args  # ValueError, якщо аргументів не 2
    book.add(name=name, phone=phone)
    return pick_message(CONTACT_ADDED_MESSAGES)


@input_error(value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES)
def change_contact(args: List[str], book: AddressBook) -> str:
    """Оновлює номер телефону."""
    name, phone = args
    book.change(name=name, phone=phone)
    return pick_message(CONTACT_UPDATED_MESSAGES)


@input_error(index_error_messages=ENTER_NAME_MESSAGES)
def show_phone(args: List[str], book: AddressBook) -> str:
    """Показує телефон контакту."""
    name = args[0]  # IndexError, якщо немає імені
    contact = book.get(name)
    return f"{contact['name']}: {contact['phone']} 📞🙂"


@input_error()
def show_all(_args: List[str], book: AddressBook) -> str:
    """Показує всі контакти."""
    items = book.all()
    if not items:
        return pick_message(NO_CONTACTS_MESSAGES)

    lines: List[str] = []
    for c in items:
        lines.append(f"{c['name']}: {c['phone']}")
    return "\n".join(lines)


@input_error(value_error_messages=ENTER_COMMAND_ARGUMENTS_MESSAGES)
def search_contacts(args: List[str], book: AddressBook) -> str:
    """Пошук за ім'ям або телефоном (частковий збіг)."""
    query = " ".join(args).strip()
    if not query:
        raise ValueError("Empty query")

    results = book.search(query)
    if not results:
        return pick_message(SEARCH_NO_RESULTS_MESSAGES)

    lines = [f"{c['name']}: {c['phone']}" for c in results]
    return "\n".join(lines)


@input_error(value_error_messages=ENTER_COMMAND_ARGUMENTS_MESSAGES)
def rename_contact(args: List[str], book: AddressBook) -> str:
    """Перейменовує контакт без зміни телефону."""
    old_name, new_name = args  # ValueError, якщо аргументів не 2
    book.rename(old_name=old_name, new_name=new_name)
    return pick_message(RENAME_SUCCESS_MESSAGES)


@input_error(index_error_messages=ENTER_NAME_MESSAGES)
def remove_contact(args: List[str], book: AddressBook) -> str:
    """Видаляє контакт без підтвердження (підтвердження робиться в main)."""
    name = args[0]
    book.remove(name)
    return pick_message(REMOVE_SUCCESS_MESSAGES)


@input_error()
def show_stats(_args: List[str], book: AddressBook) -> str:
    """Показує статистику адресної книги."""
    stats = book.stats()
    header = pick_message(STATS_HEADER_MESSAGES)
    lines = [
        header,
        f"• Contacts: {stats['contacts_count']} 📇🙂",
        f"• Unique phones: {stats['unique_phones_count']} 📞✅",
        f"• Last change: {stats['last_modified']} ⏱️📝",
    ]
    return "\n".join(lines)


# =========================
# ГОЛОВНИЙ ЦИКЛ
# =========================

def main() -> None:
    """Точка входу."""
    base_dir = Path(__file__).parent
    setup_logging(base_dir)

    data_path = base_dir / "contacts.json"
    legacy_txt = base_dir / "contacts.txt"

    book = load_address_book(
        json_path=data_path,
        legacy_txt_path=legacy_txt,
        allow_duplicate_phones=ALLOW_DUPLICATE_PHONES,
    )

    logging.info("Bot started. contacts=%s", len(book.all()))
    print(pick_message(WELCOME_MESSAGES))

    empty_input_count = 0

    command_handlers: Dict[str, Callable[[List[str], AddressBook], str]] = {
        "hello": say_hello,
        "help": show_help,
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "search": search_contacts,
        "rename": rename_contact,
        "remove": remove_contact,
        "delete": remove_contact,  # alias
        "stats": show_stats,
    }

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command == "":
            empty_input_count += 1
            print(pick_message(ENTER_COMMAND_ARGUMENTS_MESSAGES) if empty_input_count == 1 else "")
            # Показуємо м'який UX: повідомлення + авто-help
            if empty_input_count % AUTO_HELP_EVERY_EMPTY_INPUTS == 0:
                print()
                print(HELP_MESSAGE)
            continue

        empty_input_count = 0

        if command in ("close", "exit"):
            print(pick_message(GOODBYE_MESSAGES))
            logging.info("Bot exited normally.")
            break

        handler = command_handlers.get(command)
        if handler is None:
            print(pick_message(INVALID_COMMAND_MESSAGES))
            logging.warning("Invalid command: %s", command)
            continue

        # Підтвердження небезпечної дії (remove/delete)
        if command in ("remove", "delete"):
            if not args:
                print(pick_message(ENTER_NAME_MESSAGES))
                continue

            name = args[0]
            print(pick_message(CONFIRM_REMOVE_MESSAGES).format(name=name))
            confirm = input("Type YES to confirm: ").strip()
            if confirm != "YES":
                print(pick_message(OPERATION_CANCELLED_MESSAGES))
                logging.info("Remove cancelled: %s", name)
                continue

        result = handler(args, book)
        print(result)

        # Автозбереження: якщо книга змінена — зберігаємо
        if book.is_dirty:
            save_address_book(data_path, book)
            logging.info("Contacts saved. contacts=%s", len(book.all()))


if __name__ == "__main__":
    main()