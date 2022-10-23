from sqlalchemy import Column, Integer, String, Float
from app.models import Base


class DriverLocation(Base):
    __tablename__ = 'DriversLocation'
    email = Column(String[50], primary_key=True)
    street_name = Column(String[50])
    street_num = Column(Integer)
