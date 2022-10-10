import app.models.destination_models as destination_models
from app.models.destination_models import Destination
from sqlalchemy.orm import Session
from fastapi import HTTPException


def create_dst_for_user(useremail, dst, street_name, street_num, db: Session):
    # TODO: caso en que el dst ya existe para ese usuario
    db_location = Destination(
        email=useremail,
        destination=dst,
        street_name=street_name,
        street_num=street_num,
    )
    try:
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def get_address_by_dst(useremail, dst, db: Session):
    db_destination = db.query(Destination).filter(Destination.email == useremail).filter(Destination.destination == dst)
    return db_destination
