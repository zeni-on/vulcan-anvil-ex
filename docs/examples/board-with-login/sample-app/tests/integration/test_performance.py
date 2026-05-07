import time

from tests.conftest import auth_headers, login, signup


def test_PT_001_post_list_response_time(client):
    """PT-001: post list responds within the sample threshold."""
    signup(client)
    token = login(client)
    headers = auth_headers(token)
    for index in range(20):
        client.post("/api/posts", json={"title": f"Post {index}", "content": "Body"}, headers=headers)

    start = time.perf_counter()
    response = client.get("/api/posts")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 500
