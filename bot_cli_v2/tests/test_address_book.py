from address_book import AddressBook
from exceptions import ContactNotFoundError, DuplicateNameError, DuplicatePhoneError


def test_add_and_get():
    book = AddressBook({}, allow_duplicate_phones=False)
    book.add("Bob", "+380501234567")
    assert book.get("Bob") == "+380501234567"


def test_duplicate_name():
    book = AddressBook({}, allow_duplicate_phones=False)
    book.add("Bob", "+1111111111")
    try:
        book.add("Bob", "+2222222222")
    except DuplicateNameError:
        assert True
    else:
        raise AssertionError()


def test_duplicate_phone_blocked():
    book = AddressBook({}, allow_duplicate_phones=False)
    book.add("Bob", "+1111111111")
    try:
        book.add("Ann", "+1111111111")
    except DuplicatePhoneError:
        assert True
    else:
        raise AssertionError()


def test_remove_not_found():
    book = AddressBook({}, allow_duplicate_phones=False)
    try:
        book.remove("Missing")
    except ContactNotFoundError:
        assert True
    else:
        raise AssertionError()
