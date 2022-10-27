from pydantic import BaseModel, EmailStr


class TripState(BaseModel):
    trip_id: int
    driver_email: str