from fastapi import APIRouter, Depends

from app.cruds.drivers_cruds import save_driver_location_db
from app.cruds.location_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from app.schemas.drivers_schemas import DriverLocationSchema

router = APIRouter()


url_base = os.getenv('USERS_BASE_URL')


@router.post("/last_location", status_code=status.HTTP_200_OK)
def save_last_location(driver: DriverLocationSchema, db: Session = Depends(get_db)):
    save_driver_location_db(driver, db)
    return {"message": "Saved successfully"}
