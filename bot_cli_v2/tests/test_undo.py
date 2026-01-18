from pathlib import Path

from core import AppService


def test_add_and_undo(tmp_path: Path):
    data_dir = tmp_path
    svc = AppService(data_dir, enable_backups=False)

    svc.add("Alice", "+380501112233")
    assert any(r["name"] == "Alice" for r in svc.all())

    svc.undo()
    assert not any(r["name"] == "Alice" for r in svc.all())


def test_remove_and_undo(tmp_path: Path):
    data_dir = tmp_path
    svc = AppService(data_dir, enable_backups=False)
    svc.add("Bob", "+380501112244")
    assert any(r["name"] == "Bob" for r in svc.all())

    svc.remove("Bob")
    assert not any(r["name"] == "Bob" for r in svc.all())

    svc.undo()
    assert any(r["name"] == "Bob" for r in svc.all())
