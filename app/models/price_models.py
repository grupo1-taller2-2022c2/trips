from sqlalchemy import Column, Integer, String, Boolean
from app.models import Base


class PriceParams(Base):
    __tablename__ = 'PriceParams'
    version = Column(Integer, primary_key=True, autoincrement=True)