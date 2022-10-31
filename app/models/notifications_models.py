from sqlalchemy import Column, Integer, String, Float
from app.models import Base


class Token(Base):
    __tablename__ = 'NotificationToken'
    email = Column(String[50], primary_key=True)
    token = Column(String[50])
