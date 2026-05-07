import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import post, user  # noqa: F401, E402


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.state.testing_session_factory = TestingSessionLocal
    with TestClient(app) as test_client:
        yield test_client
    del app.state.testing_session_factory
    app.dependency_overrides.clear()


def signup(client: TestClient, email: str = "user@example.com", name: str = "User") -> dict:
    response = client.post(
        "/api/auth/signup",
        json={"email": email, "password": "password123", "user_name": name},
    )
    assert response.status_code == 201
    return response.json()["data"]


def login(client: TestClient, email: str = "user@example.com") -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
