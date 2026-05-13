from sqlalchemy import (Column, Integer, String, Date, SmallInteger, Text,
                        ForeignKey, Decimal, DateTime, func)
from shared.database import Base

class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False, index=True)
    work_id = Column(String(50), nullable=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=True)
    release_date = Column(Date, nullable=True)
    duration = Column(SmallInteger, nullable=True)
    cover_image = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    genres = Column(Text, nullable=True)
    cast_ids = Column(Text, nullable=True)
    rating = Column(Decimal(2, 1), nullable=True)
    source_url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
