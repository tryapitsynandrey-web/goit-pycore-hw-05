from fastapi.testclient import TestClient


def test_note_and_birthday_update_and_delete(tmp_path, monkeypatch):
    monkeypatch.setenv("AB_DATA_DIR", str(tmp_path))
    from api_server import app

    client = TestClient(app)

    # створити контакт
    payload = {"name": "Eve", "phone": "+380501230010"}
    r = client.post("/contacts", json=payload)
    assert r.status_code == 201

    # оновити з датою народження та нотаткою
    update = {
        "name": "Eve",
        "phone": "+380501230010",
        "birthday": "1992-12-01",
        "notes": "Colleague",
    }
    r = client.put("/contacts/Eve", json=update)
    assert r.status_code == 200

    # отримати і перевірити
    r = client.get("/contacts/Eve")
    assert r.status_code == 200
    data = r.json()
    assert data.get("birthday") == "1992-12-01"
    assert data.get("notes") == "Colleague"

    # видалити і перевірити
    r = client.delete("/contacts/Eve")
    assert r.status_code == 200

    r = client.get("/contacts/Eve")
    assert r.status_code == 404
