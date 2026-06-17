from tests.test_todos import make_client


def test_reg_002_ui_shell_and_static_assets_load(tmp_path, monkeypatch):
    """REG-002/UI-001: root page and static JavaScript are available for the TODO UI."""
    client = make_client(tmp_path, monkeypatch)

    page = client.get("/")
    assert page.status_code == 200
    assert "todo-form" in page.text
    assert "todo-list" in page.text

    script = client.get("/static/app.js")
    assert script.status_code == 200
    assert "loadTodos" in script.text
