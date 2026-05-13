from sqlalchemy import Column, Integer, String, Text, DateTime, func
from shared.database import Base

class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    country = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    logo = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
