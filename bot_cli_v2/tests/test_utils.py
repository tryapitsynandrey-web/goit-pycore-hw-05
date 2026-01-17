from utils import normalize_phone, validate_name


def test_validate_name_ok():
    assert validate_name(" Bob ") == "Bob"


def test_validate_name_empty():
    try:
        validate_name("   ")
    except ValueError:
        assert True
    else:
        assert False


def test_normalize_phone_plus_kept():
    assert normalize_phone("+380501234567") == "+380501234567"


def test_normalize_phone_00_to_plus():
    assert normalize_phone("00380501234567") == "+380501234567"


def test_normalize_phone_local_to_default_cc():
    assert normalize_phone("0501234567", default_country_code="+38").startswith("+38")