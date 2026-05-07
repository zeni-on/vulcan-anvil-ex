from tests.conftest import auth_headers, login, signup


def test_IT_003_list_to_detail_flow(client):
    """IT-003: a post from the list can be fetched by detail API."""
    signup(client)
    token = login(client)
    created = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(token),
    ).json()["data"]

    listed = client.get("/api/posts").json()["data"][0]
    detail = client.get(f"/api/posts/{listed['id']}").json()["data"]

    assert listed["id"] == created["id"]
    assert detail["content"] == "Body"


def test_IT_004_login_then_create_post(client):
    """IT-004: logged-in user can create a post through API."""
    signup(client)
    token = login(client)

    response = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["data"]["title"] == "Title"


def test_IT_005_authority_flow(client):
    """IT-005: author authority is enforced across update/delete APIs."""
    signup(client, "author@example.com", "Author")
    author_token = login(client, "author@example.com")
    created = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(author_token),
    ).json()["data"]
    signup(client, "other@example.com", "Other")
    other_token = login(client, "other@example.com")

    assert client.delete(f"/api/posts/{created['id']}", headers=auth_headers(other_token)).status_code == 403
    assert client.delete(f"/api/posts/{created['id']}", headers=auth_headers(author_token)).status_code == 200
