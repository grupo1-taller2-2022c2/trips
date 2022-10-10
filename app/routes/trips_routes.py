from fastapi import APIRouter, Depends
from app.cruds.destination_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests

router = APIRouter()


@router.get("/address_validation/{street_address}+{street_num}", status_code=status.HTTP_200_OK)
def validate_address(street_address: str, street_num: int):
    if not address_exists(street_address, street_num):
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return


@router.get("/dst_validation/{useremail}/{dst_name}", status_code=status.HTTP_201_CREATED)
def validate_dst(useremail: str, dst: str, db: Session = Depends(get_db)):
    address_db = get_address_by_dst(useremail, dst, db)
    if not address_db:
        raise HTTPException(
            status_code=404, detail="The location doesn't exist")
    return {"street_name": address_db.street_name, "street_num": address_db.street_num}


@router.get("/reg_cost/{src_address}+{src_number}&{dst_address}+{dst_number}", status_code=status.HTTP_200_OK)
def cost_between_two_points(src_address: str, src_number: int, dst_address: str, dst_number: int):
    if (not address_exists(src_address, src_number)) or (not address_exists(dst_address, dst_number)):
        raise HTTPException(
            status_code=404, detail="The locations aren't valid")
    distance = calculate_distance(src_address, src_number, dst_address, dst_number)  # TODO
    cost = 500 + distance * 5
    return {"cost": cost}


@router.get("/drivers_lookup/{src_address}+{src_number}&{dst_address}+{dst_number}", status_code=status.HTTP_200_OK)
def look_for_driver(src_address: str, src_number: int, dst_address: str, dst_number: int):
    # TODO
    return


def address_exists(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url)

    if response.ok:
        return True, response.json()[0]
    else:
        return False, None


def calculate_distance(src_address: str, src_number: int, dst_address: str, dst_number: int):
    # TODO
    return 0
