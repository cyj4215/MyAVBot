from sqlalchemy import Column, Integer, String, Date, SmallInteger, Text, Enum as SAEnum, DateTime, func
from shared.database import Base
import enum

class ActressStatus(str, enum.Enum):
    active = "active"
    retired = "retired"
    unknown = "unknown"

class Actress(Base):
    __tablename__ = "actresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    aliases = Column(Text, nullable=True)
    birthday = Column(Date, nullable=True)
    birthplace = Column(String(100), nullable=True)
    height = Column(SmallInteger, nullable=True)
    measurements = Column(String(50), nullable=True)
    bust = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    career_start = Column(SmallInteger, nullable=True)
    bio_text = Column(Text, nullable=True)
    profile_image = Column(String(500), nullable=True)
    social_links = Column(Text, nullable=True)
    status = Column(SAEnum(ActressStatus), default=ActressStatus.unknown)
    source_url = Column(String(500), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
