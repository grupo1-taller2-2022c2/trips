from unittest.mock import Mock, patch


def test_address_validation_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        # Mockeo la llamada a la api externa de Google
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = ["El address es valido"]

        response = client.get(
            "/trips/address_validation/?street_address=Mendoza&street_num=1000"
        )

    assert response.status_code == 200, response.text


def test_address_validation_not_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        # Mockeo la llamada a la api externa de Google
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = []

        response = client.get(
            "/trips/address_validation/?street_address=Mendoza&street_num=111111111"
        )

    assert response.status_code == 200, response.text
