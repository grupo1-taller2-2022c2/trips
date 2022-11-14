from pydantic import BaseModel


class ExpoToken(BaseModel):
    email: str
    token: str
