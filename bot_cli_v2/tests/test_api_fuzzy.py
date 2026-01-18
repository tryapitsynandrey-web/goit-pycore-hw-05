from fastapi.testclient import TestClient


def test_api_fuzzy_search_create_and_find(tmp_path, monkeypatch):
    # Запустити API з ізольованою директорією даних, щоб уникнути конфліктів з існуючими даними
    monkeypatch.setenv("AB_DATA_DIR", str(tmp_path))

    # імпортувати app після встановлення змінної оточення
    from api_server import app

    client = TestClient(app)

    # створити контакт
    payload = {"name": "Charlie", "phone": "+380501234999"}
    r = client.post("/contacts", json=payload)
    assert r.status_code == 201

    # нечіткий пошук за частковим іменем
    r = client.get("/fsearch", params={"query": "Char"})
    assert r.status_code == 200
    data = r.json()
    assert any(d.get("name") == "Charlie" for d in data)
