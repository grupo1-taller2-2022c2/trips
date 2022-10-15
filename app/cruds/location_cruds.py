import app.models.location_models as destination_models
from app.models.location_models import *
from sqlalchemy.orm import Session
from fastapi import HTTPException


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
