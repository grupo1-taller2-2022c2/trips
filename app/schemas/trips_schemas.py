from typing import Union, List, Optional
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


class LocationCreate(BaseModel):
    email: str
    location: str
    street_name: str
    street_num: int


class PriceChange(BaseModel):
    base: Optional[float] = None
    distance: Optional[float] = None
    duration: Optional[float] = None
    days_of_week: List[str]
    busy_hours: List[int]
    busy_hours_extra: Optional[float] = None
    week_day_extra: Optional[float] = None
    passenger_rating: Optional[float] = None
