from tests.conftest import signup


def test_IT_001_signup_then_login(client):
    """IT-001: signup result can be used for login."""
    signup(client)

    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})

    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


def test_IT_002_authenticated_endpoint_requires_token(client):
    """IT-002: authenticated features require a token."""
    response = client.post("/api/posts", json={"title": "Title", "content": "Body"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ERR-003"
