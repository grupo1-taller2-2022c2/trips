from typing import Union
import datetime
from sqlalchemy.sql import func
import app.models.trips_models as destination_models
from app.models.trips_models import *
from sqlalchemy.orm import Session
from fastapi import HTTPException


def get_travel_history_from_db(passenger_email, db: Session):
    return db.query(Trip).filter(Trip.passenger_email == passenger_email).order_by(Trip.id.desc()).all()[:5]


def create_loc_for_user(useremail, loc, street_name, street_num, db: Session):
    # TODO: caso en que el dst ya existe para ese usuario
    db_location = SavedLocation(
        email=useremail,
        location=loc,
        street_name=street_name,
        street_num=street_num,
    )
    try:
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def get_address_by_loc(useremail, loc, db: Session):
    db_location = db.query(SavedLocation).filter(SavedLocation.email == useremail).filter(SavedLocation.location == loc)
    return db_location


def create_trip_info(src_address, src_number, dst_address, dst_number, passenger_email, cost,
                     trip_type: Union[str, None], db: Session):
    if trip_type is None:
        trip_type = "Regular"
    db_trip = Trip(
        src_address = src_address,
        src_number = src_number,
        dst_address = dst_address,
        dst_number = dst_number,
        passenger_email = passenger_email,
        price = cost,
        type = trip_type,
        state = "Not initialized",
    )
    try:
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return db_trip.id
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def get_trip_from_id(trip_id: int, db: Session):
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail=f"The trip with id {trip_id} doesn't exist")
    return db_trip


def initialize_trip_db(trip_id: int, driver_email: str, db: Session):
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    try:
        db_trip.driver_email = driver_email
        db_trip.date = func.now()
        db_trip.state = "In course"
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def deny_trip_db(trip_id: int, driver_email: str, db: Session):
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    try:
        db_trip.driver_email = driver_email
        db_trip.date = func.now()
        db_trip.state = "Denied"
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def finalize_trip_db(trip_id: int, db: Session):
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    try:
        db_trip.state = "Completed"
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")
