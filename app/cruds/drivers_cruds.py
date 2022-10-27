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
    driver_db = db.query(DriverLocation).filter(DriverLocation.email == driver.email).first()
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


def change_driver_state(driver_email: str, db: Session):
    driver_db = db.query(DriverLocation).filter(DriverLocation.email == driver_email).first()
    try:
        driver_db.state = "driving"
        db.commit()
        return
    except Exception as _:
        raise HTTPException(status_code=500, detail="Internal server error")
