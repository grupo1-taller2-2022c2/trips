from fastapi import APIRouter, Depends

from app.cruds.notifications_cruds import save_user_token, delete_token, get_token_from_db
from app.cruds.trips_cruds import *
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from app.database import get_db
import requests
import os
from typing import Union
from app.schemas.notifications_schemas import ExpoToken
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

router = APIRouter()


@router.post("/token/", status_code=status.HTTP_201_CREATED)
def save_expo_token(token: ExpoToken, db: Session = Depends(get_db)):
    save_user_token(token.token, token.email, db)
    return {"message": "Saved Successfully"}


@router.delete("/token/{email}", status_code=status.HTTP_202_ACCEPTED)
def delete_expo_token(email: str, db: Session = Depends(get_db)):
    delete_token(email, db)
    return {"message": "Deleted Successfully"}


def send_push_message(email, title, message, db: Session, extra=None):
    token = get_token_from_db(email, db)
    try:
        PushClient().publish(PushMessage(to=token,
                                         title=title,
                                         body=message,
                                         data=extra))
    except Exception as _:
        return
    """except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        raise"""
