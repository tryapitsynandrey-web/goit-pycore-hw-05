from datetime import date, timedelta

from fastapi.testclient import TestClient


def test_upcoming_birthdays(tmp_path, monkeypatch):
    # використовувати ізольовану директорію даних
    monkeypatch.setenv("AB_DATA_DIR", str(tmp_path))
    # імпортувати app після встановлення змінних оточення
    from api_server import app as imported_app

    client = TestClient(imported_app)

    today = date.today()
    in_3 = (today + timedelta(days=3)).isoformat()
    in_10 = (today + timedelta(days=10)).isoformat()

    # створити контакти
    r = client.post(
        "/contacts", json={"name": "Soon", "phone": "+380501230001", "birthday": in_3}
    )
    assert r.status_code == 201
    r = client.post(
        "/contacts", json={"name": "Later", "phone": "+380501230002", "birthday": in_10}
    )
    assert r.status_code == 201

    # запит майбутніх за наступні 7 днів -> має включати "Soon", але не "Later"
    r = client.get("/birthdays", params={"days": 7})
    assert r.status_code == 200
    data = r.json()
    names = [d.get("name") for d in data]
    assert "Soon" in names
    assert "Later" not in names
