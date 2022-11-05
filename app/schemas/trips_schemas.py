from typing import Union

from pydantic import BaseModel, EmailStr


class TripState(BaseModel):
    trip_id: int
    driver_email: str
    status: str


class TripCreate(BaseModel):
    src_address: str
    src_number: int
    dst_address: str
    dst_number: int
    passenger_email: str
    duration: float
    distance: float
    trip_type: Union[str, None]
