from fastapi import APIRouter, Depends

from app.cruds.drivers_cruds import save_driver_location_db, get_driver_location_by_email, \
    delete_drivers_last_location_db, get_drivers_assigned_trip_db, delete_drivers_assigned_trip_db
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os

from app.routes.notifications_routes import send_push_message
from app.schemas.drivers_schemas import DriverLocationSchema, DriverLocationDelete
import geopy.distance

router = APIRouter()


url_base = os.getenv('USERS_BASE_URL')


@router.post("/last_location", status_code=status.HTTP_200_OK)
def save_last_location(driver: DriverLocationSchema, db: Session = Depends(get_db)):
    save_driver_location_db(driver, db)
    return {"message": "Saved successfully"}


@router.get("/last_location/{driveremail}", status_code=status.HTTP_200_OK)
def gat_drivers_last_location(driveremail: str, db: Session = Depends(get_db)):
    return get_driver_location_by_email(driveremail, db)


@router.delete("/last_location/", status_code=status.HTTP_200_OK)
def delete_drivers_last_location(driveremail: DriverLocationDelete, db: Session = Depends(get_db)):
    return delete_drivers_last_location_db(driveremail.email, db)


@router.get("/assigned_trip/{driveremail}", status_code=status.HTTP_200_OK)
def gat_drivers_assigned_trip(driveremail: str, db: Session = Depends(get_db)):
    trip_id = get_drivers_assigned_trip_db(driveremail, db)
    passenger_email = get_trip_from_id(trip_id, db).passenger_email
    url = url_base + "/passengers/" + passenger_email
    response = requests.get(url=url)
    if response.ok:
        return {"trip_id": trip_id, "passenger": response.json()}
    delete_drivers_assigned_trip_db(driveremail, db)
    send_push_message(email=passenger_email, title="Trip Cancelled",
                      message=f"The trip with id {trip_id} was cancelled due to internal error.", db=db)


def calculate_distance(src_address, src_number, dst_address, dst_number):
    coord1 = get_latitude_and_longitude(src_address, src_number)
    coord2 = get_latitude_and_longitude(dst_address, dst_number)
    return geopy.distance.geodesic(coord1, coord2).km


def get_latitude_and_longitude(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url).json()

    if len(response) != 0:
        return response[0]["lat"], response[0]["lon"]
    else:
        return None
