from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.models import Base


class Trip(Base):
    __tablename__ = 'Trips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    src_address = Column(String(50), nullable=False)
    src_number = Column(Integer, nullable=False)
    dst_address = Column(String(50), nullable=False)
    dst_number = Column(Integer, nullable=False)
    passenger_email = Column(String(50), nullable=False)
    driver_email = Column(String(50), nullable=True)
    date = Column(DateTime)
    price = Column(Float, nullable=False)
    type = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)


class SavedLocation(Base):
    __tablename__ = 'SavedLocation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    location = Column(String(50), nullable=False)
    street_name = Column(String(50), nullable=False)
    street_num = Column(Integer, nullable=False)