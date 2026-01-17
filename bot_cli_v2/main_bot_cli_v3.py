from __future__ import annotations

import logging
import random
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

from address_book import AddressBook
from storage import load_contacts_json, migrate_txt_to_json_if_needed, save_contacts_json
from utils import format_contacts_table, format_stats_box, normalize_phone
from ux_messages import (
    AUTO_HELP_EVERY_EMPTY_INPUTS,
    CONTACT_ADDED_MESSAGES,
    CONTACT_REMOVED_MESSAGES,
    CONTACT_UPDATED_MESSAGES,
    DUPLICATE_NAME_MESSAGES,
    DUPLICATE_PHONE_MESSAGES,
    EMPTY_INPUT_MESSAGES,
    ENTER_COMMAND_ARGUMENTS_MESSAGES,
    ENTER_NAME_AND_PHONE_MESSAGES,
    ENTER_NAME_MESSAGES,
    GOODBYE_MESSAGES,
    HELP_MESSAGE,
    INVALID_COMMAND_MESSAGES,
    NO_CONTACTS_MESSAGES,
    REMOVE_CANCELED_MESSAGES,
    REMOVE_CONFIRM_MESSAGES,
    WELCOME_MESSAGES,
)

# =========================
# LOGGING
# =========================


def setup_logging(base_dir: Path) -> None:
    """Налаштовує логування у файл у папці проєкту."""
    log_path = base_dir / "logfile.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
    )


# =========================
# HELPERS
# =========================


def pick_message(messages: Sequence[str]) -> str:
    """Повертає випадкове повідомлення з набору."""
    return random.choice(messages)


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Розбиває введення на команду та аргументи."""
    cleaned = user_input.strip()
    if not cleaned:
        return "", []
    parts = cleaned.split()
    return parts[0].lower(), parts[1:]


def get_empty_input_message(empty_count: int) -> str:
    """Повертає повідомлення для порожнього вводу (Enter без команди)."""
    index = empty_count % len(EMPTY_INPUT_MESSAGES)
    return EMPTY_INPUT_MESSAGES[index]


def require_record(book: AddressBook, name: str) -> dict:
    """Повертає record контакту або кидає KeyError (щоб декоратор відпрацював)."""
    record = book.get_record(name)
    if not isinstance(record, dict):
        raise KeyError(name)
    return record


def extract_records_from_book(book: AddressBook) -> List[dict]:
    """Повертає список записів для виводу (табличкою)."""
    data = book.to_dict()
    if not isinstance(data, dict):
        return []

    records: List[dict] = []
    for name in sorted(data):
        rec = data.get(name)
        if isinstance(rec, dict):
            copy_rec = dict(rec)
            copy_rec.setdefault("name", name)
            records.append(copy_rec)

    return records


# =========================
# INPUT ERROR DECORATOR
# =========================


def input_error(
    *,
    index_error_messages: Sequence[str] | None = None,
    key_error_messages: Sequence[str] | None = None,
    value_error_messages: Sequence[str] | None = None,
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Декоратор для обробки помилок введення користувача (IndexError/KeyError/ValueError)."""

    index_msgs = index_error_messages or ENTER_COMMAND_ARGUMENTS_MESSAGES
    key_msgs = key_error_messages or ("Contact not found.",)
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
# COMMAND HANDLERS
# =========================


@input_error(value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES)
def add_contact(args: List[str], book: AddressBook) -> str:
    """add <name> <phone>"""
    name, raw_phone = args
    phone = normalize_phone(raw_phone)

    try:
        book.add(name, phone)
    except ValueError as e:
        msg = str(e).lower()
        if "duplicate name" in msg:
            return pick_message(DUPLICATE_NAME_MESSAGES)
        if "duplicate phone" in msg:
            return pick_message(DUPLICATE_PHONE_MESSAGES)
        raise

    return pick_message(CONTACT_ADDED_MESSAGES)


@input_error(value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES, key_error_messages=("Contact not found.",))
def change_contact(args: List[str], book: AddressBook) -> str:
    """change <name> <phone>"""
    name, raw_phone = args
    phone = normalize_phone(raw_phone)

    _ = require_record(book, name)

    try:
        book.change(name, phone)
    except ValueError as e:
        msg = str(e).lower()
        if "duplicate phone" in msg:
            return pick_message(DUPLICATE_PHONE_MESSAGES)
        raise

    return pick_message(CONTACT_UPDATED_MESSAGES)


@input_error(index_error_messages=ENTER_NAME_MESSAGES, key_error_messages=("Contact not found.",))
def show_phone(args: List[str], book: AddressBook) -> str:
    """phone <name>"""
    name = args[0]
    record = require_record(book, name)
    record.setdefault("name", name)
    return format_contacts_table([record])


@input_error()
def show_all(_args: List[str], book: AddressBook) -> str:
    """all"""
    records = extract_records_from_book(book)
    if not records:
        return pick_message(NO_CONTACTS_MESSAGES)
    return format_contacts_table(records)


@input_error(value_error_messages=("Please provide a search query.",))
def search_contact(args: List[str], book: AddressBook) -> str:
    """search <query>"""
    query = " ".join(args).strip()
    results = book.search(query)

    if not results:
        return "No matches found."

    records: List[dict] = []
    for rec in results:
        if isinstance(rec, dict):
            copy_rec = dict(rec)
            copy_rec.setdefault("name", str(copy_rec.get("name", "")).strip())
            records.append(copy_rec)

    if not records:
        return "No matches found."

    return format_contacts_table(records)


@input_error(
    value_error_messages=("Please provide old and new name.",),
    key_error_messages=("Contact not found.",),
)
def rename_contact(args: List[str], book: AddressBook) -> str:
    """rename <old> <new>"""
    old_name, new_name = args
    _ = require_record(book, old_name)

    try:
        book.rename(old_name, new_name)
    except ValueError as e:
        msg = str(e).lower()
        if "duplicate name" in msg:
            return pick_message(DUPLICATE_NAME_MESSAGES)
        raise

    return "✍️🙂 Renamed successfully. =)"


@input_error(index_error_messages=ENTER_NAME_MESSAGES, key_error_messages=("Contact not found.",))
def remove_contact(args: List[str], book: AddressBook) -> str:
    """remove <name> / delete <name>"""
    name = args[0]
    _ = require_record(book, name)

    confirm_prompt = pick_message(REMOVE_CONFIRM_MESSAGES)
    answer = input(confirm_prompt).strip().upper()

    if answer != "YES":
        return pick_message(REMOVE_CANCELED_MESSAGES)

    book.remove(name)
    return pick_message(CONTACT_REMOVED_MESSAGES)


@input_error()
def show_stats(_args: List[str], book: AddressBook) -> str:
    """stats"""
    return format_stats_box(book.stats())


@input_error()
def say_hello(_args: List[str], _book: AddressBook) -> str:
    """hello"""
    return "How can I help you? 🙂👋"


@input_error()
def show_help(_args: List[str], _book: AddressBook) -> str:
    """help"""
    return HELP_MESSAGE


# =========================
# MAIN LOOP
# =========================


def main() -> None:
    base_dir = Path(__file__).parent
    setup_logging(base_dir)
    logging.info("Bot started")

    migrate_txt_to_json_if_needed(base_dir)

    contacts_path = base_dir / "contacts.json"
    contacts_dict, last_modified = load_contacts_json(contacts_path)

    book = AddressBook(allow_duplicate_phones=False)
    book.load_from_dict(contacts_dict, last_modified=last_modified)

    empty_input_count = 0

    command_handlers: Dict[str, Callable[[List[str], AddressBook], str]] = {
        "hello": say_hello,
        "help": show_help,
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "remove": remove_contact,
        "delete": remove_contact,
        "search": search_contact,
        "rename": rename_contact,
        "stats": show_stats,
    }

    print(pick_message(WELCOME_MESSAGES))
    logging.info("Welcome message shown")

    while True:
        try:
            user_input = input("Enter a command: ")
        except (KeyboardInterrupt, EOFError):
            print()
            print(pick_message(GOODBYE_MESSAGES))
            logging.info("Bot exited by Ctrl+C / EOF")
            break

        command, args = parse_input(user_input)

        if command == "":
            print(get_empty_input_message(empty_input_count))
            empty_input_count += 1

            if empty_input_count % AUTO_HELP_EVERY_EMPTY_INPUTS == 0:
                print()
                print(HELP_MESSAGE)

            continue

        empty_input_count = 0

        if command in ("close", "exit"):
            print(pick_message(GOODBYE_MESSAGES))
            logging.info("Bot exited by user command")
            break

        handler = command_handlers.get(command)
        if handler is None:
            print(pick_message(INVALID_COMMAND_MESSAGES))
            logging.warning("Invalid command: %s", command)
            continue

        logging.info("Command: %s | args=%s", command, args)
        result = handler(args, book)
        print(result)

        # Автозбереження після команд, що змінюють дані
        if command in ("add", "change", "remove", "delete", "rename"):
            save_contacts_json(contacts_path, book.to_dict(), book.last_modified)
            logging.info("Contacts saved to JSON (atomic)")

    logging.info("Bot finished")


if __name__ == "__main__":
    main()