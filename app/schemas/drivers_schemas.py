from pydantic import BaseModel, EmailStr


class DriverLocationSchema(BaseModel):
    email: EmailStr
    street_name: str
    street_num: int
