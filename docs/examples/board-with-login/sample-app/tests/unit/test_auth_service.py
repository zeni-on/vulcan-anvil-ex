from app.core.security import verify_password
from app.repositories.user_repository import UserRepository

from tests.conftest import signup


def test_UT_001_signup_success(client):
    """UT-001 / AC-001: normal signup stores a password hash."""
    user = signup(client)
    assert user["email"] == "user@example.com"
    assert user["user_name"] == "User"


def test_UT_002_duplicate_email_blocked(client):
    """UT-002 / AC-002: duplicate email is blocked with ERR-001."""
    signup(client)
    response = client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "password123", "user_name": "Other"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ERR-001"


def test_UT_003_login_success(client):
    """UT-003 / AC-003: login succeeds with the correct password."""
    signup(client)
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["data"]["token_type"] == "bearer"


def test_UT_004_login_failure(client):
    """UT-004 / AC-004: login failure uses a controlled message code."""
    signup(client)
    response = client.post("/api/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ERR-002"


def test_UT_001_password_not_stored_as_plain_text(client):
    """SEC-001: password is hashed before persistence."""
    signup(client)
    session = client.app.state.testing_session_factory()
    try:
        user = UserRepository(session).get_by_email("user@example.com")
        assert user is not None
        assert user.password_hash != "password123"
        assert verify_password("password123", user.password_hash)
    finally:
        session.close()
