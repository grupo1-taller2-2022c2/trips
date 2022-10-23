from fastapi import APIRouter, Depends
from app.cruds.location_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os

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


@router.get("/address_validation/{street_address}+{street_num}", status_code=status.HTTP_200_OK)
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


@router.get("/reg_cost/{src_address}+{src_number}&"
            "{dst_address}+{dst_number}&"
            "{driver_email}&{passenger_email}&"
            "{duration}&{distance}&{location}&"
            "{date}&{hour}", status_code=status.HTTP_200_OK)
def cost_between_two_points(src_address: str, src_number: int, dst_address: str, dst_number: int, driver_email: str,
                            passenger_email: str, duration: float, distance: float, location: str, date, hour):
    if (not address_exists(src_address, src_number)) or (not address_exists(dst_address, dst_number)):
        raise HTTPException(
            status_code=404, detail="The locations aren't valid")
    cost = PRICING.calculate(distance, duration)
    return {"cost": cost}


def address_exists(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url)

    if response.ok:
        return True, response.json()[0]
    else:
        return False, None
