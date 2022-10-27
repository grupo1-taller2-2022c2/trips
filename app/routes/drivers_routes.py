from fastapi import APIRouter, Depends

from app.cruds.drivers_cruds import save_driver_location_db, get_driver_location_by_email
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from app.schemas.drivers_schemas import DriverLocationSchema
import geopy.distance

router = APIRouter()


url_base = os.getenv('USERS_BASE_URL')


@router.post("/last_location", status_code=status.HTTP_200_OK)
def save_last_location(driver: DriverLocationSchema, db: Session = Depends(get_db)):
    save_driver_location_db(driver, db)
    return {"message": "Saved successfully"}


@router.get("/driver_lookup/", status_code=status.HTTP_200_OK)
def look_for_driver(trip_id: int, db: Session = Depends(get_db)):
    url = url_base + "/drivers/all_available"
    db_trip = get_trip_from_id(trip_id, db)
    response = requests.get(url=url)
    if response.ok:
        distance = 0
        driver_info = None
        for driver in response.json():
            driver_db = get_driver_location_by_email(driver["email"], db)
            if not driver_db or driver_db.state == "driving":
                continue
            new_distance = calculate_distance(db_trip.src_address, db_trip.src_number, driver_db.street_name, driver_db.street_num)
            if (new_distance < distance) or (driver_info is None):
                distance = new_distance
                driver_info = driver

        return driver_info
    raise HTTPException(status_code=response.status_code,
                        detail=response.json()['detail'])


def calculate_distance(src_address, src_number, dst_address, dst_number):
    coord1 = get_latitude_and_longitude(src_address, src_number)
    coord2 = get_latitude_and_longitude(dst_address, dst_number)
    return geopy.distance.geodesic(coord1, coord2).km


def get_latitude_and_longitude(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url)

    if response.ok:
        return response.json()[0]["lat"], response.json()[0]["lon"]
    else:
        return None
