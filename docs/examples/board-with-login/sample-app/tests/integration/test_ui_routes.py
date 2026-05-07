def test_UI_001_screen_routes_return_app_shell(client):
    """UI-001~UI-006: screen routes return the SPA shell."""
    routes = ["/", "/signup", "/login", "/posts", "/posts/new", "/posts/1", "/posts/1/edit"]

    for route in routes:
        response = client.get(route)

        assert response.status_code == 200
        assert 'id="app"' in response.text
        assert "/assets/app.js" in response.text


def test_UI_007_assets_are_served(client):
    """UI-007: static assets are available for browser rendering."""
    response = client.get("/assets/styles.css")

    assert response.status_code == 200
    assert ".page" in response.text
    assert ".panel" in response.text
