from unittest.mock import Mock, patch
import requests
import requests_mock
adapter = requests_mock.Adapter()
s = requests.Session()
s.mount('mock://', adapter)


class ApiMock:
    def __init__(self, json_value):
        self.ok = True
        self.text = str(json_value)
        self.json_value = json_value

    def json(self):
        return self.json_value


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

    assert response.status_code == 404, response.text


def test_travel_history_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        response = client.get(
            "/trips/history/test_email@gmail.com"
        )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_driver_travel_history_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        response = client.get(
            "/trips/history/test_email@gmail.com/?user_type=driver"
        )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_saved_location_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        location = {
            "email": "test_email@gmail.com",
            "location": "school",
            "street_name": "Paseo colon",
            "street_num": 850
        }
        response = client.post(
            "/trips/saved_location/",
            json=location
        )

    assert response.status_code == 201, response.text
    assert response.json()["message"] == "Saved successfully"


def test_get_saved_location_not_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        response = client.get(
            "/trips/saved_location/test_email@gmail.com/school"
        )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "The location doesn't exist"


def test_get_saved_location_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        location = {
            "email": "test_email@gmail.com",
            "location": "school",
            "street_name": "Paseo colon",
            "street_num": 850
        }
        client.post(
            "/trips/saved_location/",
            json=location
        )
        response = client.get(
            "/trips/saved_location/test_email@gmail.com/school"
        )

    assert response.status_code == 200, response.text
    assert response.json()["street_name"] == "Paseo colon"
    assert response.json()["street_num"] == 850


def test_get_all_saved_location_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        response = client.get(
            "/trips/saved_location/test_email@gmail.com/"
        )

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_create_trip_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True
        adapter.register_uri('GET', '/passengers/test_email@gmail.com', json={"ratings": 5})
        adapter.register_uri('GET', '/drivers/all_available', text="[]")

        trip = {
            "src_address": "paseo colon",
            "src_number": 850,
            "dst_address": "paseo colon",
            "dst_number": 850,
            "passenger_email": "test_email@gmail.com",
            "duration": 1,
            "distance": 1
        }
        response = client.post(
            "/trips/",
            json=trip
        )

    assert response.status_code == 201, response.text
    assert response.json()[0] == 1
    assert response.json()[1] is None


def test_create_trip_with_driver_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        # Create a notif token for driver
        token = {
            "email": "test_driver@gmail.com",
            "token": "test_token"
        }

        client.post(
            "/notifications/token/",
            json=token
        )
        # Mock api calls
        mock_rating = ApiMock({"ratings": 5})
        mock_id = ApiMock('139722651300288')
        mock_balance = ApiMock({"balance": 1})
        mock_driver = ApiMock([{"email": "test_driver@gmail.com"}])
        mock_get.side_effect = [mock_rating, mock_id, mock_balance, mock_driver]

        driver = {
            "email": "test_driver@gmail.com",
            "street_name": "paseo colon",
            "street_num": 840
        }
        client.post(
            "/drivers/last_location",
            json=driver,
        )
        trip = {
            "src_address": "paseo colon",
            "src_number": 850,
            "dst_address": "paseo colon",
            "dst_number": 850,
            "passenger_email": "test_email@gmail.com",
            "duration": 1,
            "distance": 1
        }
        response = client.post(
            "/trips/",
            json=trip
        )

    assert response.status_code == 201, response.text
    assert response.json()[0] == 1
    assert response.json()[1]["email"] == "test_driver@gmail.com"


def test_get_trip_info_not_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        response = client.get(
            "/trips/1"
        )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "The trip with id 1 doesn't exist"


def test_get_trip_info_ok(client):
    with patch("app.routes.trips_routes.requests.get") as mock_get:
        mock_get.return_value.ok = True

        trip = {
            "src_address": "paseo colon",
            "src_number": 850,
            "dst_address": "paseo colon",
            "dst_number": 850,
            "passenger_email": "test_email@gmail.com",
            "duration": 1,
            "distance": 1
        }
        client.post(
            "/trips/",
            json=trip
        )
        response = client.get(
            "/trips/1"
        )

    assert response.status_code == 200, response.text
    assert response.json()["src_address"] == "paseo colon"
    assert response.json()["src_number"] == 850
    assert response.json()["dst_address"] == "paseo colon"
    assert response.json()["dst_number"] == 850
    assert response.json()["passenger_email"] == "test_email@gmail.com"

