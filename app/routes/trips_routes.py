from fastapi import APIRouter, Depends

from app.cruds.drivers_cruds import change_driver_state, get_driver_location_by_email
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from typing import Union

from app.routes.drivers_routes import calculate_distance
from app.schemas.trips_schemas import TripState, TripCreate, LocationCreate

router = APIRouter()


url_base = os.getenv('USERS_BASE_URL')


class Pricing:
    def __init__(self):
        self.base = 400
        self.distance = 0.1
        self.duration = 0.1

    def calculate(self, distance, duration):
        return self.base + self.distance * distance + self.duration * duration


PRICING = Pricing()


@router.get("/history/{email}", status_code=status.HTTP_200_OK)
def get_travel_history(email: str, user_type: Union[str, None] = None, db: Session = Depends(get_db)):
    if user_type == "driver":
        return get_driver_travel_history_from_db(email, db)
    return get_passenger_travel_history_from_db(email, db)


@router.get("/address_validation/", status_code=status.HTTP_200_OK)
def validate_address(street_address: str, street_num: int):
    if not address_exists(street_address, street_num):
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return


@router.get("/saved_location/{useremail}/{location_name}", status_code=status.HTTP_200_OK)
def get_passenger_saved_location(useremail: str, location_name: str, db: Session = Depends(get_db)):
    address_db = get_address_by_loc(useremail, location_name, db)
    if not address_db:
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return {"street_name": address_db.street_name, "street_num": address_db.street_num}


@router.get("/saved_location/{useremail}/", status_code=status.HTTP_200_OK)
def get_all_passenger_saved_location(useremail: str, db: Session = Depends(get_db)):
    address_db = get_all_locations_by_email(useremail, db)
    return address_db


@router.post("/saved_location/", status_code=status.HTTP_201_CREATED)
def add_passenger_saved_location(location: LocationCreate, db: Session = Depends(get_db)):
    create_location_for_user(location.email, location.location, location.street_name, location.street_num, db)
    return {"message": "Saved successfully"}


@router.get("/cost/", status_code=status.HTTP_200_OK)
def calculate_cost(src_address: str, src_number: int, dst_address: str, dst_number: int, passenger_email: str, duration: float,
                   distance: float, trip_type: Union[str, None] = None, db: Session = Depends(get_db)):
    address_exist, address = address_exists(src_address, src_number)
    if not address_exist:
        raise HTTPException(
            status_code=404, detail="The location isn't valid")
    price = PRICING.calculate(distance, duration)
    return {"price": price}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trip_and_driver_lookup(trip: TripCreate, db: Session = Depends(get_db)):
    url = url_base + "/drivers/all_available"
    response = requests.get(url=url)
    price = PRICING.calculate(trip.distance, trip.duration)
    trip_id = create_trip_info(trip.src_address, trip.src_number, trip.dst_address, trip.dst_number,
                               trip.passenger_email, price, trip.trip_type, db)
    if response.ok:
        distance = 0
        driver_info = None
        for driver in response.json():
            driver_db = get_driver_location_by_email(driver["email"], db)
            if (not driver_db) or (driver_db.state == "driving"):
                continue
            new_distance = calculate_distance(trip.src_address, trip.src_number, driver_db.street_name, driver_db.street_num)
            if (new_distance < distance) or (driver_info is None):
                distance = new_distance
                driver_info = driver
        # TODO: send notification to driver
        # TODO: maybe assign trip to driver
        return trip_id, driver_info
    raise HTTPException(status_code=response.status_code,
                        detail=response.json()['detail'])


@router.get("/{trip_id}", status_code=status.HTTP_200_OK)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return get_trip_from_id(trip_id, db)


@router.patch("/", status_code=status.HTTP_200_OK)
def change_trip_state(trip: TripState, db: Session = Depends(get_db)):
    if trip.status == "Accept":
        accept_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "driving", db)
        # TODO: SEND NOTIFICATION TO PASSENGER
        return {"message": "Trip accepted"}
    if trip.status == "Deny":
        deny_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "free", db)
        # TODO: SEND NOTIFICATION TO PASSENGER
        return {"message": "Trip denied"}
    if trip.status == "Initialize":
        driver_db = get_driver_location_by_email(trip.driver_email, db)
        trip_db = get_trip_from_id(trip.trip_id, db)
        check_distance(driver_db.street_name, driver_db.street_num, trip_db.src_address, trip_db.src_number)
        initialize_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "driving", db)
        # TODO: SEND NOTIFICATION TO PASSENGER
        return {"message": "Trip initialized"}
    if trip.status == "Finalize":
        driver_db = get_driver_location_by_email(trip.driver_email, db)
        trip_db = get_trip_from_id(trip.trip_id, db)
        check_distance(driver_db.street_name, driver_db.street_num, trip_db.src_address, trip_db.src_number)
        finalize_trip_db(trip.trip_id, db)
        change_driver_state(trip.driver_email, "free", db)
        # TODO: SEND NOTIFICATION TO PASSENGER
        return {"message": "Trip finalized"}
    raise HTTPException(status_code=400, detail="The valid status are: Accept, Deny, Initialize, Finalize")


def address_exists(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url).json()

    if len(response) != 0:
        return True, response[0]
    else:
        return False, None


def check_distance(address_1, number_1, address_2, number_2):
    distance = calculate_distance(address_1, number_1, address_2, number_2)
    if distance > 0.1:
        raise HTTPException(status_code=400, detail="The driver has not arrived to the correct place")
