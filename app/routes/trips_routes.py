from app.cruds.wallets_cruds import can_pay_trip, make_payment
from fastapi import APIRouter, Depends
from app.cruds.drivers_cruds import (
    change_driver_state,
    get_driver_location_by_email,
    save_drivers_assigned_trip_db,
    delete_drivers_assigned_trip_db,
)
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from typing import Union

from app.routes.drivers_routes import calculate_distance
from app.routes.notifications_routes import send_push_message
from app.schemas.trips_schemas import TripState, TripCreate, LocationCreate, PriceChange

from app.utils.pricing import Pricing

router = APIRouter()


url_base = os.getenv("USERS_BASE_URL")


PRICING = Pricing()


@router.get("/history/{email}", status_code=status.HTTP_200_OK)
def get_travel_history(
    email: str, user_type: Union[str, None] = None, db: Session = Depends(get_db)
):
    histories = []
    if user_type == "driver":
        trips = get_driver_travel_history_from_db(email, db)
        for trip in trips:
            trip = dict(trip.__dict__)
            url = url_base + "/passengers/" + trip["passenger_email"]
            response = requests.get(url=url)
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])
            history = {
                "username": response.json()["username"],
                "surname": response.json()["surname"],
                "ratings": response.json()["ratings"]
            }
            trip["info"] = history
            histories.append(trip)
        return histories
    trips = get_passenger_travel_history_from_db(email, db)
    for trip in trips:
        trip = dict(trip.__dict__)
        url = url_base + "/drivers/" + trip["driver_email"]
        response = requests.get(url=url)
        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])
        history = {
            "username": response.json()["username"],
            "surname": response.json()["surname"],
            "ratings": response.json()["ratings"]
        }
        trip["info"] = history
        histories.append(trip)
    return histories


@router.get("/address_validation/", status_code=status.HTTP_200_OK)
def validate_address(street_address: str, street_num: int):
    if not address_exists(street_address, street_num):
        raise HTTPException(status_code=404, detail="The location doesn't exist")
    return


@router.get(
    "/saved_location/{useremail}/{location_name}", status_code=status.HTTP_200_OK
)
def get_passenger_saved_location(
    useremail: str, location_name: str, db: Session = Depends(get_db)
):
    address_db = get_address_by_loc(useremail, location_name, db)
    if not address_db:
        raise HTTPException(status_code=404, detail="The location doesn't exist")
    return {"street_name": address_db.street_name, "street_num": address_db.street_num}


@router.get("/saved_location/{useremail}/", status_code=status.HTTP_200_OK)
def get_all_passenger_saved_location(useremail: str, db: Session = Depends(get_db)):
    address_db = get_all_locations_by_email(useremail, db)
    return address_db


@router.post("/saved_location/", status_code=status.HTTP_201_CREATED)
def add_passenger_saved_location(
    location: LocationCreate, db: Session = Depends(get_db)
):
    create_location_for_user(
        location.email, location.location, location.street_name, location.street_num, db
    )
    return {"message": "Saved successfully"}


@router.get("/cost/", status_code=status.HTTP_200_OK)
def calculate_cost(
    src_address: str,
    src_number: int,
    dst_address: str,
    dst_number: int,
    passenger_email: str,
    duration: float,
    distance: float,
    trip_type: Union[str, None] = None
):
    url = url_base + "/passengers/" + passenger_email
    response = requests.get(url=url)
    if response.ok:
        price = PRICING.calculate(distance, duration, float(response.json()["ratings"]))
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])
    return {"price": price}


@router.patch("/cost/", status_code=status.HTTP_200_OK)
def modify_cost_rule(price_change: PriceChange):
    PRICING.change_pricing(price_change)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trip_and_driver_lookup(trip: TripCreate, db: Session = Depends(get_db)):
    url = url_base + "/passengers/" + trip.passenger_email
    response = requests.get(url=url)
    if response.ok:
        price = PRICING.calculate(trip.distance, trip.duration, float(response.json()["ratings"]))
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json()["detail"])

    if not can_pay_trip(trip.passenger_email, price):
        message = "Not enough balance in wallet to pay trip"
        raise HTTPException(status_code=400, detail=message)

    url = url_base + "/drivers/all_available"
    response = requests.get(url=url)

    trip_db = create_trip_info(
        trip.src_address,
        trip.src_number,
        trip.dst_address,
        trip.dst_number,
        trip.passenger_email,
        price,
        trip.trip_type,
        db,
    )
    if response.ok:
        distance = 0
        driver_info = None
        for driver in response.json():
            driver_db = get_driver_location_by_email(driver["email"], db)
            if (not driver_db) or (driver_db.state == "driving"):
                continue
            new_distance = calculate_distance(
                trip.src_address,
                trip.src_number,
                driver_db.street_name,
                driver_db.street_num,
            )
            if (new_distance < distance) or (driver_info is None):
                distance = new_distance
                driver_info = driver
        if not driver_info:
            return trip_db.id, None
        send_push_message(
            email=driver_info["email"],
            title="Trip Request",
            message=f"You-ve received a trip request from the passenger {trip.passenger_email}.",
            db=db,
            extra={"trip_id": trip_db.id},
        )
        assign_trip_db(trip_db.id, driver_info["email"], db)
        change_driver_state(driver_info["email"], "assigned", db)
        save_drivers_assigned_trip_db(driver_info["email"], trip_db.id, db)
        return trip_db.id, driver_info
    raise HTTPException(
        status_code=response.status_code, detail=response.json()["detail"]
    )


@router.get("/{trip_id}", status_code=status.HTTP_200_OK)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return get_trip_from_id(trip_id, db)


@router.patch("/", status_code=status.HTTP_200_OK)
def change_trip_state(trip: TripState, db: Session = Depends(get_db)):
    if trip.status == "Accept":
        passenger_email = accept_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "driving", db)
        delete_drivers_assigned_trip_db(trip.driver_email, db)
        send_push_message(
            email=passenger_email,
            title="Trip Accepted",
            message="The driver has accepted the trip.",
            db=db,
        )
        return {"message": "Trip accepted"}
    if trip.status == "Deny":
        passenger_email = deny_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "free", db)
        delete_drivers_assigned_trip_db(trip.driver_email, db)
        send_push_message(
            email=passenger_email,
            title="Trip Denied",
            message="The driver has denied the trip.",
            db=db,
        )
        return {"message": "Trip denied"}
    if trip.status == "Initialize":
        driver_db = get_driver_location_by_email(trip.driver_email, db)
        trip_db = get_trip_from_id(trip.trip_id, db)
        check_distance(
            driver_db.street_name,
            driver_db.street_num,
            trip_db.src_address,
            trip_db.src_number,
        )
        passenger_email = initialize_trip_db(trip.trip_id, trip.driver_email, db)
        change_driver_state(trip.driver_email, "driving", db)
        send_push_message(
            email=passenger_email,
            title="Trip Initialized",
            message="The driver has arrived.",
            db=db,
        )
        return {"message": "Trip initialized"}
    if trip.status == "Finalize":
        driver_db = get_driver_location_by_email(trip.driver_email, db)
        trip_db = get_trip_from_id(trip.trip_id, db)
        check_distance(
            driver_db.street_name,
            driver_db.street_num,
            trip_db.dst_address,
            trip_db.dst_number,
        )
        make_payment(trip_db.passenger_email, trip_db.driver_email, trip_db.price)

        passenger_email = finalize_trip_db(trip.trip_id, db)
        change_driver_state(trip.driver_email, "free", db)
        send_push_message(
            email=passenger_email,
            title="Trip Finalized",
            message="The trip has finalized.",
            db=db,
        )
        return {"message": "Trip finalized"}
    raise HTTPException(
        status_code=400,
        detail="The valid status are: Accept, Deny, Initialize, Finalize",
    )


@router.get("/pricing/", status_code=status.HTTP_200_OK)
def get_pricing():
    pricing = {
        "base": PRICING.base,
        "distance": PRICING.distance,
        "duration": PRICING.duration,
        "days_of_week": PRICING.days_of_week,
        "busy_hours": PRICING.busy_hours,
        "busy_hours_extra": PRICING.busy_hours_extra,
        "week_day_extra": PRICING.week_day_extra,
        "passenger_rating": PRICING.passenger_rating
    }
    return pricing


def address_exists(street_address: str, street_num: int):
    city = "Buenos Aires"
    country = "Argentina"
    url = f"https://nominatim.openstreetmap.org/?addressdetails=1&street={street_address}+{street_num}&city={city}&country={country}&format=json&limit=1"

    response = requests.get(url).json()

    if len(response) != 0:
        return True
    else:
        return False


def check_distance(address_1, number_1, address_2, number_2):
    distance = calculate_distance(address_1, number_1, address_2, number_2)
    if distance > 0.1:
        raise HTTPException(
            status_code=400, detail="The driver has not arrived to the correct place"
        )
