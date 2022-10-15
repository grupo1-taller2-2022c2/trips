from sqlalchemy import Column, Integer, String, Boolean
from app.models import Base


class SavedLocation(Base):
    __tablename__ = 'SavedLocation'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), nullable=False)
    location = Column(String(50), nullable=False)
    street_name = Column(String(50), nullable=False)
    street_num = Column(Integer, nullable=False)