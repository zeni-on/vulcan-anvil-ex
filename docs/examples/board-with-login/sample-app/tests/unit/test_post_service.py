from tests.conftest import auth_headers, login, signup


def test_UT_005_post_list_newest_first(client):
    """UT-005 / AC-005: posts are listed newest first."""
    signup(client)
    token = login(client)
    headers = auth_headers(token)
    first = client.post("/api/posts", json={"title": "First", "content": "Content"}, headers=headers).json()["data"]
    second = client.post("/api/posts", json={"title": "Second", "content": "Content"}, headers=headers).json()["data"]

    response = client.get("/api/posts")

    assert response.status_code == 200
    ids = [post["id"] for post in response.json()["data"]]
    assert ids[:2] == [second["id"], first["id"]]


def test_UT_006_post_detail_fields(client):
    """UT-006 / AC-006: detail returns title, content, author, timestamps."""
    signup(client)
    token = login(client)
    created = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(token),
    ).json()["data"]

    response = client.get(f"/api/posts/{created['id']}")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Title"
    assert data["content"] == "Body"
    assert data["author_id"] == created["author_id"]
    assert data["created_at"]


def test_UT_007_authenticated_user_can_create_post(client):
    """UT-007 / AC-007: authenticated user can create a post."""
    signup(client)
    token = login(client)

    response = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["data"]["title"] == "Title"


def test_UT_008_anonymous_user_cannot_create_post(client):
    """UT-008 / AC-008: anonymous post creation is blocked."""
    response = client.post("/api/posts", json={"title": "Title", "content": "Body"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ERR-003"


def test_UT_009_author_can_update_post(client):
    """UT-009 / AC-009: author can update a post."""
    signup(client)
    token = login(client)
    created = client.post(
        "/api/posts",
        json={"title": "Before", "content": "Body"},
        headers=auth_headers(token),
    ).json()["data"]

    response = client.put(
        f"/api/posts/{created['id']}",
        json={"title": "After", "content": "Updated"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "After"


def test_UT_010_author_can_delete_post(client):
    """UT-010 / AC-010: author can delete a post."""
    signup(client)
    token = login(client)
    created = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(token),
    ).json()["data"]

    response = client.delete(f"/api/posts/{created['id']}", headers=auth_headers(token))

    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True
    assert client.get(f"/api/posts/{created['id']}").status_code == 404


def test_UT_011_other_user_cannot_modify_or_delete(client):
    """UT-011 / AC-011: another user cannot modify or delete a post."""
    signup(client, "author@example.com", "Author")
    author_token = login(client, "author@example.com")
    created = client.post(
        "/api/posts",
        json={"title": "Title", "content": "Body"},
        headers=auth_headers(author_token),
    ).json()["data"]
    signup(client, "other@example.com", "Other")
    other_token = login(client, "other@example.com")

    update_response = client.put(
        f"/api/posts/{created['id']}",
        json={"title": "Hack", "content": "No"},
        headers=auth_headers(other_token),
    )
    delete_response = client.delete(f"/api/posts/{created['id']}", headers=auth_headers(other_token))

    assert update_response.status_code == 403
    assert update_response.json()["error"]["code"] == "ERR-004"
    assert delete_response.status_code == 403
    assert delete_response.json()["error"]["code"] == "ERR-004"
