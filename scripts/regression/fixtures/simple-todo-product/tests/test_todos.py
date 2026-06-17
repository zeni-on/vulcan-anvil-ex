import importlib

from fastapi.testclient import TestClient


def make_client(tmp_path, monkeypatch):
    """Create an isolated client using a temp DB for SCN-001~003 regression tests."""
    monkeypatch.setenv("TODO_DB_PATH", str(tmp_path / "todos.db"))
    import app.main as main

    importlib.reload(main)
    return TestClient(main.app)


def test_scn_001_create_and_list_todo(tmp_path, monkeypatch):
    """SCN-001/REG-001: input '문서 정리' -> list contains one incomplete Todo."""
    client = make_client(tmp_path, monkeypatch)

    created = client.post("/api/todos", json={"text": "문서 정리"})
    assert created.status_code == 201
    assert created.json()["data"]["text"] == "문서 정리"

    listed = client.get("/api/todos")
    assert listed.status_code == 200
    assert listed.json()["data"][0]["completed"] is False


def test_scn_002_toggle_completed(tmp_path, monkeypatch):
    """SCN-002/REG-001: completed True request -> response and list show completed True."""
    client = make_client(tmp_path, monkeypatch)
    todo = client.post("/api/todos", json={"text": "테스트"}).json()["data"]

    updated = client.patch(f"/api/todos/{todo['id']}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["data"]["completed"] is True


def test_scn_003_delete_todo(tmp_path, monkeypatch):
    """SCN-003/REG-001: delete existing Todo -> list becomes empty."""
    client = make_client(tmp_path, monkeypatch)
    todo = client.post("/api/todos", json={"text": "삭제 대상"}).json()["data"]

    deleted = client.delete(f"/api/todos/{todo['id']}")
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deleted"] is True
    assert client.get("/api/todos").json()["data"] == []


def test_validation_rejects_blank_text(tmp_path, monkeypatch):
    """API-002/Product security baseline: blank input -> no stack trace, 422 error."""
    client = make_client(tmp_path, monkeypatch)

    response = client.post("/api/todos", json={"text": "   "})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "TODO_TEXT_INVALID"
