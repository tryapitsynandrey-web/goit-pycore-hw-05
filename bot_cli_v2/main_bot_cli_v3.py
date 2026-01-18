from __future__ import annotations

import csv
import random
import shlex
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

from address_book import AddressBook
from core import AppService
from exceptions import (
    ContactNotFoundError,
    DuplicateNameError,
    DuplicatePhoneError,
    ValidationError,
)
from logger_setup import setup_logger
from settings import SETTINGS
from storage import (
    migrate_txt_to_json_if_needed,
    save_contacts_json,
)
from telemetry import record_command
from utils import (
    format_contacts_table,
    format_stats_box,
    normalize_phone,
    validate_birthday,
)
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
# ЛОГУВАННЯ
# =========================


def setup_logging(base_dir: Path):
    """Return configured logger (assistant_bot)."""
    log_path = base_dir / "logfile.log"
    return setup_logger(log_path)


# =========================
# ДОПОМОЖНІ ФУНКЦІЇ
# =========================


def pick_message(messages: Sequence[str]) -> str:
    """Повертає випадкове повідомлення з набору."""
    return random.choice(messages)


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    """Розбиває введення на команду та аргументи.

    Підтримує лапки для багатослівних аргументів, наприклад:
    add "John Doe" "+380501234567"
    """
    cleaned = (user_input or "").strip()
    if not cleaned:
        return "", []

    try:
        parts = shlex.split(cleaned)
    except ValueError:
        # У разі помилки — як запасний варіант розбиваємо по пробілах
        parts = cleaned.split()

    if not parts:
        return "", []

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
# ДЕКОРАТОР ОБРОБКИ ПОМИЛОК ВВЕДЕННЯ
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
            except (KeyError, ContactNotFoundError):
                return pick_message(key_msgs)
            except (
                ValueError,
                ValidationError,
                DuplicateNameError,
                DuplicatePhoneError,
            ):
                return pick_message(value_msgs)

        return inner

    return decorator


# =========================
# ОБРОБНИКИ КОМАНД
# =========================


@input_error(value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES)
def add_contact(args: List[str], book: AddressBook) -> str:
    """add <name> <phone>"""
    name, raw_phone = args
    phone = normalize_phone(
        raw_phone, default_country_code=SETTINGS.default_country_code
    )

    try:
        book.add(name, phone)
    except DuplicateNameError:
        return pick_message(DUPLICATE_NAME_MESSAGES)
    except DuplicatePhoneError:
        return pick_message(DUPLICATE_PHONE_MESSAGES)

    return pick_message(CONTACT_ADDED_MESSAGES)


@input_error(
    value_error_messages=ENTER_NAME_AND_PHONE_MESSAGES,
    key_error_messages=("Contact not found.",),
)
def change_contact(args: List[str], book: AddressBook) -> str:
    """change <name> <phone>"""
    name, raw_phone = args
    phone = normalize_phone(
        raw_phone, default_country_code=SETTINGS.default_country_code
    )

    _ = require_record(book, name)

    try:
        book.change(name, phone)
    except DuplicatePhoneError:
        return pick_message(DUPLICATE_PHONE_MESSAGES)

    return pick_message(CONTACT_UPDATED_MESSAGES)


@input_error(
    index_error_messages=ENTER_NAME_MESSAGES, key_error_messages=("Contact not found.",)
)
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


@input_error(value_error_messages=("Please provide days as integer (optional).",))
def list_birthdays_cli(args: List[str], book: AddressBook) -> str:
    """birthdays [days] - list upcoming birthdays (default 7 days)"""
    svc = getattr(book, "_service", None)
    if svc is None:
        from core import AppService

        svc = AppService(Path(__file__).parent)
        svc.book = book

    days = 7
    if args:
        try:
            days = int(args[0])
        except Exception:
            raise ValueError("Invalid days")

    results = svc.upcoming_birthdays(days=days)
    if not results:
        return "No upcoming birthdays."
    return format_contacts_table(results)


@input_error(index_error_messages=("Please provide filename.",))
def export_birthdays_cli(args: List[str], book: AddressBook) -> str:
    """birthdays_export <filename.csv> [days] - export upcoming birthdays to CSV"""
    fname = args[0]
    days = 7
    if len(args) > 1:
        try:
            days = int(args[1])
        except Exception:
            raise ValueError("Invalid days")

    svc = getattr(book, "_service", None)
    if svc is None:
        from core import AppService

        svc = AppService(Path(__file__).parent)
        svc.book = book

    results = svc.upcoming_birthdays(days=days)
    path = Path(fname)
    import csv

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["name", "phone", "birthday", "days_until", "notes"]
        )
        writer.writeheader()
        for r in results:
            writer.writerow(
                {
                    "name": r.get("name", ""),
                    "phone": r.get("phone", ""),
                    "birthday": r.get("birthday", ""),
                    "days_until": r.get("days_until", ""),
                    "notes": r.get("notes", ""),
                }
            )

    return f"Exported {len(results)} upcoming birthdays to {path}"


@input_error(index_error_messages=("Please provide filename.",))
def export_contacts(args: List[str], book: AddressBook) -> str:
    """export <filename.csv> - export contacts to CSV"""
    fname = args[0]
    path = Path(fname)

    records = book.all_records_sorted()
    if not records:
        return pick_message(NO_CONTACTS_MESSAGES)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "name",
                "phone",
                "birthday",
                "notes",
                "created_at",
                "updated_at",
            ],
        )
        writer.writeheader()
        for r in records:
            writer.writerow(
                {
                    "name": r.get("name", ""),
                    "phone": r.get("phone", ""),
                    "birthday": r.get("birthday", ""),
                    "notes": r.get("notes", ""),
                    "created_at": r.get("created_at", ""),
                    "updated_at": r.get("updated_at", ""),
                }
            )

    return f"Exported {len(records)} contacts to {path}"


@input_error(index_error_messages=("Please provide filename.",))
def import_contacts(args: List[str], book: AddressBook) -> str:
    """import <filename.csv> - import contacts from CSV (skips duplicates)"""
    fname = args[0]
    path = Path(fname)
    if not path.is_file():
        return "File not found."

    # Віддавати перевагу транзакційному імпорту, якщо на книзі є AppService
    svc = getattr(book, "_service", None)
    if svc is not None and hasattr(svc, "import_csv"):
        # svc.import_csv очікує Path і зафіксує одну операцію undo для всього імпорту
        try:
            # Нормалізація телефонів всередині сервісного імпорту не застосовується —
            # переконайтесь, що CSV містить нормалізовані номери або покладіться на перевірки AddressBook
            res = svc.import_csv(path)
        except FileNotFoundError:
            return "File not found."
        else:
            return f"Imported: {res.get('added', 0)} added, {res.get('skipped', 0)} skipped."

    # Запасний варіант: покроковий імпорт по рядках (зберігає стару поведінку)
    added = 0
    skipped = 0
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = str(row.get("name", "")).strip()
            phone = str(row.get("phone", "")).strip()
            birthday = str(row.get("birthday", "")).strip() or None
            notes = str(row.get("notes", "")).strip() or None
            if not name or not phone:
                skipped += 1
                continue
            try:
                normalized = normalize_phone(
                    phone, default_country_code=SETTINGS.default_country_code
                )
                book.add(name, normalized, birthday=birthday, notes=notes)
                added += 1
            except Exception:
                skipped += 1

    return f"Imported: {added} added, {skipped} skipped."


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


@input_error(
    index_error_messages=ENTER_NAME_MESSAGES, key_error_messages=("Contact not found.",)
)
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


@input_error(value_error_messages=("Please provide name and birthday in YYYY-MM-DD.",))
def set_birthday(args: List[str], book: AddressBook) -> str:
    """setbday <name> <YYYY-MM-DD>"""
    name, bday = args
    # валідація і застосування
    b = validate_birthday(bday)
    # вимагаємо, щоб контакт існував
    _ = require_record(book, name)
    # використовуємо поточний номер щоб зберегти його
    phone = book.get(name)
    book.change(name, phone, birthday=b)
    return "Birthday updated."


@input_error(value_error_messages=("Please provide name and note.",))
def set_note(args: List[str], book: AddressBook) -> str:
    """setnote <name> <note>"""
    name, note = args
    _ = require_record(book, name)
    phone = book.get(name)
    book.change(name, phone, notes=note)
    return "Note updated."


@input_error(
    index_error_messages=ENTER_NAME_MESSAGES, key_error_messages=("Contact not found.",)
)
def clear_note(args: List[str], book: AddressBook) -> str:
    """clearnote <name>"""
    name = args[0]
    _ = require_record(book, name)
    phone = book.get(name)
    # встановити порожню нотатку
    book.change(name, phone, notes="")
    return "Note cleared."


# =========================
# ГОЛОВНИЙ ЦИКЛ
# =========================


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="assistant-bot", description="Simple address book assistant"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(Path(__file__).parent),
        help="Path to data directory",
    )
    parser.add_argument(
        "--allow-duplicates", action="store_true", help="Allow duplicate phone numbers"
    )
    parser.add_argument(
        "--no-backups",
        action="store_true",
        help="Disable automatic backups when saving data",
    )
    args = parser.parse_args()

    base_dir = Path(args.data_dir)
    logger = setup_logging(base_dir)
    logger.info("Bot started")

    enable_backups = not getattr(args, "no_backups", False)

    # если ваша функция миграции принимает enable_backups — оставляем; иначе уберите аргумент
    migrate_txt_to_json_if_needed(base_dir, enable_backups=enable_backups)

    # Создаём AppService и получаем книгу из него
    service = AppService(
        base_dir,
        enable_backups=enable_backups,
        allow_duplicate_phones=args.allow_duplicates,
    )
    book = service.book
    book._service = service

    empty_input_count = 0
    invalid_input_count = 0
    auto_help_n = getattr(
        SETTINGS, "auto_help_every_empty_inputs", AUTO_HELP_EVERY_EMPTY_INPUTS
    )

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
        "export": export_contacts,
        "import": import_contacts,
        "setbday": set_birthday,
        "setnote": set_note,
        "clearnote": clear_note,
        "birthdays": list_birthdays_cli,
        "birthdays_export": export_birthdays_cli,
        "undo": lambda _args, book: "",
        "redo": lambda _args, book: "",
    }

    print(pick_message(WELCOME_MESSAGES))
    logger.info("Welcome message shown")

    while True:
        try:
            user_input = input("Enter a command: ")
        except (KeyboardInterrupt, EOFError):
            print()
            print(pick_message(GOODBYE_MESSAGES))
            logger.info("Bot exited by Ctrl+C / EOF")
            break

        command, args = parse_input(user_input)

        if command == "":
            print(get_empty_input_message(empty_input_count))
            empty_input_count += 1
            if empty_input_count % auto_help_n == 0:
                print()
                print(HELP_MESSAGE)

            continue

        empty_input_count = 0

        if command in ("close", "exit"):
            print(pick_message(GOODBYE_MESSAGES))
            logger.info("Bot exited by user command")
            break

        handler = command_handlers.get(command)
        if handler is None:
            invalid_input_count += 1
            print(pick_message(INVALID_COMMAND_MESSAGES))
            logger.warning("Invalid command: %s", command)
            try:
                record_command(base_dir, f"invalid:{command}")
            except Exception:
                pass
            if invalid_input_count % auto_help_n == 0:
                print()
                print(HELP_MESSAGE)
            continue

        logger.info("Command: %s | args=%s", command, args)
        try:
            record_command(base_dir, command)
        except Exception:
            pass

        if command in ("undo", "redo"):
            try:
                # Пытаемся использовать уже подвязанный сервис
                svc = getattr(book, "_service", None)
                if svc is None:
                    # Резерв: создаём новый, БЕЗ локального импорта AppService!
                    svc = AppService(
                        base_dir,
                        enable_backups=enable_backups,
                        allow_duplicate_phones=book.allow_duplicate_phones,
                    )
                    svc.book = book

                if command == "undo":
                    svc.undo()
                else:
                    svc.redo()
                result = "OK"
            except Exception as e:
                logger.exception("Error during %s: %s", command, e)
                result = f"Error: {e}"
        else:
            try:
                result = handler(args, book)
            except Exception as e:
                logger.exception("Handler error for %s: %s", command, e)
                result = "An internal error occurred. Check logs."

        invalid_trigger = False
        try:
            if (
                result in INVALID_COMMAND_MESSAGES
                or result in ENTER_COMMAND_ARGUMENTS_MESSAGES
                or result in ENTER_NAME_MESSAGES
                or result in ENTER_NAME_AND_PHONE_MESSAGES
            ):
                invalid_trigger = True
        except Exception:
            invalid_trigger = False

        if invalid_trigger:
            invalid_input_count += 1
            if invalid_input_count % auto_help_n == 0:
                print()
                print(HELP_MESSAGE)
        else:
            invalid_input_count = 0

        print(result)

        # Автосохранение после мутаций — по возможности через сервис
        if command in (
            "add",
            "change",
            "remove",
            "delete",
            "rename",
            "setbday",
            "setnote",
            "clearnote",
        ):
            try:
                svc = getattr(book, "_service", None)
                if svc is not None:
                    svc._save()
                else:
                    contacts_path = base_dir / "contacts.json"
                    save_contacts_json(
                        contacts_path,
                        book.to_dict(),
                        book.last_modified,
                        enable_backups=enable_backups,
                    )
                logger.info("Contacts saved to JSON (atomic)")
            except Exception:
                logger.exception("Failed to autosave contacts")

    logger.info("Bot finished")

if __name__ == "__main__":
    main()