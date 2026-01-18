from address_book import AddressBook


def test_add_contact_with_birthday_and_notes():
    book = AddressBook()
    book.add("Dana", "+380501230000", birthday="1990-05-01", notes="Friend from work")
    rec = book.get_record("Dana")
    assert rec.get("name") == "Dana"
    assert rec.get("phone") == "+380501230000"
    assert rec.get("birthday") == "1990-05-01"
    assert rec.get("notes") == "Friend from work"
