from unittest.mock import Mock, patch


def test_save_token_ok(client):
    with patch("app.routes.notifications_routes.requests.post") as mock_post:
        mock_post.return_value.ok = True

        token = {
            "email": "test_email@gmail.com",
            "token": "test_token"
        }

        response = client.post(
            "/notifications/token/",
            json=token,
        )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["message"] == "Saved Successfully"


def test_update_token_ok(client):
    with patch("app.routes.notifications_routes.requests.post") as mock_post:
        mock_post.return_value.ok = True

        token = {
            "email": "test_email@gmail.com",
            "token": "test_token"
        }

        client.post(
            "/notifications/token/",
            json=token,
        )
        new_token = {
            "email": "test_email@gmail.com",
            "token": "test_token_1"
        }
        response = client.post(
            "/notifications/token/",
            json=new_token,
        )

    assert response.status_code == 201
    assert response.json()["message"] == "Saved Successfully"


def test_delete_token_not_ok(client):
    with patch("app.routes.notifications_routes.requests.delete") as mock_post:
        mock_post.return_value.ok = True

        response = client.delete(
            "/notifications/token/test_email@gmail.com"
        )

    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "The user doesn't have a valid token"


def test_delete_token_ok(client):
    with patch("app.routes.notifications_routes.requests.delete") as mock_post:
        mock_post.return_value.ok = True

        token = {
            "email": "test_email@gmail.com",
            "token": "test_token"
        }

        client.post(
            "/notifications/token/",
            json=token,
        )
        response = client.delete(
            "/notifications/token/test_email@gmail.com"
        )

    assert response.status_code == 202, response.text
    data = response.json()
    assert data["message"] == "Deleted Successfully"
