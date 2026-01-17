from __future__ import annotations


class AddressBookError(Exception):
    """Базова помилка адресної книги."""


class ContactNotFoundError(AddressBookError):
    """Контакт не знайдено."""


class DuplicateNameError(AddressBookError):
    """Ім'я вже існує."""


class DuplicatePhoneError(AddressBookError):
    """Телефон вже використовується."""


class ValidationError(AddressBookError):
    """Помилка валідації даних."""