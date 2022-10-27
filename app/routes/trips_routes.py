from fastapi import APIRouter, Depends

from app.cruds.drivers_cruds import change_driver_state
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from typing import Union

from app.schemas.trips_schemas import TripState

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


@router.get("/history/{passenger_email}", status_code=status.HTTP_200_OK)
def get_travel_history(passenger_email: str, db: Session = Depends(get_db)):
    return get_travel_history_from_db(passenger_email, db)


@router.get("/address_validation/", status_code=status.HTTP_200_OK)
def validate_address(street_address: str, street_num: int):
    if not address_exists(street_address, street_num):
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return


@router.get("/saved_loc_validation/{useremail}/{loc_name}", status_code=status.HTTP_201_CREATED)
def validate_dst(useremail: str, loc_name: str, db: Session = Depends(get_db)):
    address_db = get_address_by_loc(useremail, loc_name, db)
    if not address_db:
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return {"street_name": address_db.street_name, "street_num": address_db.street_num}


@router.get("/cost/", status_code=status.HTTP_200_OK)
def calculate_cost(src_address: str, src_number: int, dst_address: str, dst_number: int, passenger_email: str, duration: float,
                   distance: float, trip_type: Union[str, None] = None, db: Session = Depends(get_db)):
    address_exist, address = address_exists(src_address, src_number)
    if not address_exist:
        raise HTTPException(
            status_code=404, detail="The location isn't valid")
    price = PRICING.calculate(distance, duration)
    trip_id = create_trip_info(src_address, src_number, dst_address, dst_number, passenger_email, price, trip_type, db)
    return {"price": price, "trip_id": trip_id}


@router.get("/{trip_id}", status_code=status.HTTP_200_OK)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return get_trip_from_id(trip_id, db)


@router.patch("/accept", status_code=status.HTTP_200_OK)
def accept_trip(trip: TripState, db: Session = Depends(get_db)):
    change_driver_state(trip.driver_email, "driving", db)
    # TODO: SEND NOTIFICATION TO PASSENGER
    return {"message": "Trip accepted"}


@router.patch("/deny", status_code=status.HTTP_200_OK)
def deny_trip(trip: TripState, db: Session = Depends(get_db)):
    deny_trip_db(trip.trip_id, trip.driver_email, db)
    change_driver_state(trip.driver_email, "free", db)
    # TODO: SEND NOTIFICATION TO PASSENGER
    return {"message": "Trip denied"}


@router.patch("/initialize", status_code=status.HTTP_200_OK)
def initialize_trip(trip: TripState, db: Session = Depends(get_db)):
    initialize_trip_db(trip.trip_id, trip.driver_email, db)
    change_driver_state(trip.driver_email, "driving", db)
    # TODO: SEND NOTIFICATION TO PASSENGER
    return {"message": "Trip initialized"}


@router.patch("/finalize", status_code=status.HTTP_200_OK)
def finalize_trip(trip: TripState, db: Session = Depends(get_db)):
    finalize_trip_db(trip.trip_id, db)
    change_driver_state(trip.driver_email, "free", db)
    # TODO: SEND NOTIFICATION TO PASSENGER
    return {"message": "Trip finalized"}


def address_exists(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url).json()

    if len(response) != 0:
        return True, response[0]
    else:
        return False, None
