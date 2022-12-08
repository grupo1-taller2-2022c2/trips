import app.models.trips_models as destination_models
from app.models.notifications_models import Token
from app.models.trips_models import *
from app.models.drivers_models import *
from sqlalchemy.orm import Session
from fastapi import HTTPException


def save_user_token(token, email, db: Session):
    db_token = db.query(Token).filter(Token.email == email).first()
    if db_token:
        raise HTTPException(status_code=409, detail="The user already has a token")
    db_token = Token(
        email=email,
        token=token
    )
    try:
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


def delete_token(email, db: Session):
    db_token = db.query(Token).filter(Token.email == email).first()
    if not db_token:
        raise HTTPException(
            status_code=404, detail="The user doesn't have a valid token")
    try:
        db.delete(db_token)
        db.commit()
        return
    except Exception as _:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


def get_token_from_db(email, db: Session):
    db_token = db.query(Token).filter(Token.email == email).first()
    if not db_token:
        raise HTTPException(
            status_code=404, detail="The user doesn't have a valid token")
    return db_token.token


def delete_added_notifications_info(db: Session):
    try:
        db.query(Token).delete()
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Could not delete trips tokens: " + e.__str__)
