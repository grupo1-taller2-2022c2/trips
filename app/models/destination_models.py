from sqlalchemy import Column, Integer, String, Boolean
from app.models import Base


class Destination(Base):
    __tablename__ = 'Destinations'
    email = Column(String(50), nullable=False)
    destination = Column(String(50), nullable=False)
    street_name = Column(String(50), nullable=False)
    street_num = Column(Integer, nullable=False)