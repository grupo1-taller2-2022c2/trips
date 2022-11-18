import app.models.trips_models as destination_models
from app.models.trips_models import *
from app.models.drivers_models import *
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.drivers_schemas import DriverLocationSchema


def create_driver_location(driver: DriverLocationSchema, db: Session):
    db_driver = DriverLocation(
        email=driver.email,
        street_name=driver.street_name,
        street_num=driver.street_num,
        state="free",
    )
    try:
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def save_driver_location_db(driver: DriverLocationSchema, db: Session):
    driver_db = db.query(DriverLocation).filter(
        DriverLocation.email == driver.email).first()
    if not driver_db:
        create_driver_location(driver, db)
        return
    try:
        driver_db.street_name = driver.street_name
        driver_db.street_num = driver.street_num
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def get_driver_location_by_email(driver_email: str, db: Session):
    return db.query(DriverLocation).filter(DriverLocation.email == driver_email).first()


def delete_drivers_last_location_db(driver_email: str, db: Session):
    db_location = db.query(DriverLocation).filter(
        DriverLocation.email == driver_email).first()
    if not db_location:
        raise HTTPException(status_code=404, detail="The driver doesn't exist")
    try:
        db.delete(db_location)
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def change_driver_state(driver_email: str, state: str, db: Session):
    driver_db = db.query(DriverLocation).filter(
        DriverLocation.email == driver_email).first()
    try:
        driver_db.state = state
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def save_drivers_assigned_trip_db(driveremail, trip_id, db: Session):
    db_trip = DriverAssignedTrip(
        email=driveremail,
        trip_id=trip_id
    )
    try:
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def get_drivers_assigned_trip_db(driveremail, db: Session):
    db_trip = db.query(DriverAssignedTrip).filter(
        DriverAssignedTrip.email == driveremail).first()
    if not db_trip:
        raise HTTPException(
            status_code=404, detail=f"The driver hasn't any assigned trip yet")
    return db_trip.trip_id


def delete_drivers_assigned_trip_db(driveremail, db: Session):
    db_trip = db.query(DriverAssignedTrip).filter(
        DriverAssignedTrip.email == driveremail).first()
    if not db_trip:
        raise HTTPException(
            status_code=404, detail="The driver doesn't have any assigned trip")
    try:
        db.delete(db_trip)
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")


def delete_added_drivers_info(db: Session):
    try:
        db.query(DriverLocation).delete()
        db.query(DriverAssignedTrip).delete()
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Could not delete drivers location and assigned trip in trips: " + e.__str__)
