from unittest.mock import Mock, patch


def test_save_last_location_ok(client):
    with patch("app.routes.drivers_routes.requests.post") as mock_post:
        mock_post.return_value.ok = True

        driver = {
            "email": "test_email@gmail.com",
            "street_name": "test_street_name",
            "street_num": 1234
        }

        response = client.post(
            "/drivers/last_location",
            json=driver,
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Saved successfully"


def test_get_last_location_ok(client):
    with patch("app.routes.drivers_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        driver = {
            "email": "test_email@gmail.com",
            "street_name": "test_street_name",
            "street_num": 1234
        }
        client.post(
            "/drivers/last_location",
            json=driver,
        )
        response = client.get(
            "/drivers/last_location/test_email@gmail.com"
        )

    assert response.status_code == 200, response.text
    assert response.json()["email"] == "test_email@gmail.com"
    assert response.json()["street_name"] == "test_street_name"
    assert response.json()["street_num"] == 1234
    assert response.json()["state"] == "free"


def test_update_last_location_ok(client):
    with patch("app.routes.drivers_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        driver = {
            "email": "test_email@gmail.com",
            "street_name": "test_street_name",
            "street_num": 1234
        }
        client.post(
            "/drivers/last_location",
            json=driver,
        )
        # Change address
        driver["street_name"] = "test_street_name_2"
        driver["street_num"] = 4321
        client.post(
            "/drivers/last_location",
            json=driver,
        )
        # Get location
        response = client.get(
            "/drivers/last_location/test_email@gmail.com"
        )

    assert response.status_code == 200, response.text
    assert response.json()["email"] == "test_email@gmail.com"
    assert response.json()["street_name"] == "test_street_name_2"
    assert response.json()["street_num"] == 4321
    assert response.json()["state"] == "free"


def test_delete_last_location_not_ok(client):
    with patch("app.routes.drivers_routes.requests.delete") as mock_get:
        mock_get.return_value.ok = True

        driver = {
            "email": "test_email@gmail.com",
            "street_name": "test_street_name",
            "street_num": 1234
        }
        client.post(
            "/drivers/last_location",
            json=driver,
        )
        driver = {
            "email": "test_email@gmail.com"
        }
        response = client.delete(
            "/drivers/last_location/",
            json=driver,
        )

    assert response.status_code == 200, response.text


def test_delete_last_location_ok(client):
    with patch("app.routes.drivers_routes.requests.delete") as mock_get:
        mock_get.return_value.ok = True

        driver = {
            "email": "test_email@gmail.com"
        }
        response = client.delete(
            "/drivers/last_location/",
            json=driver,
        )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "The driver doesn't exist"
