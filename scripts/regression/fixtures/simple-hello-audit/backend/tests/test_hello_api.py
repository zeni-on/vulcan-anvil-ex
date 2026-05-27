import pytest

fastapi = pytest.importorskip("fastapi")

from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient

from app.api.hello import get_hello_response, router
from app.main import app


def test_IT_001_hello_route_contract_exists() -> None:
    paths = {route.path for route in router.routes}

    assert "/hello" in paths
    assert get_hello_response.__annotations__["return"] is PlainTextResponse


def test_IT_001_get_hello_returns_200_text_plain_and_hello() -> None:
    client = TestClient(app)

    response = client.get("/hello")

    assert response.status_code == 200
    assert response.text == "hello"
    assert "text/plain" in response.headers["content-type"]
