from sqlalchemy import (Column, Integer, String, BigInteger, Text,
                        Enum as SAEnum, DateTime, func)
from shared.database import Base
import enum

class MagnetCategory(str, enum.Enum):
    adult_eu = "adult_eu"
    general = "general"

class MagnetLink(Base):
    __tablename__ = "magnet_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    info_hash = Column(String(40), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_count = Column(Integer, nullable=True)
    source_site = Column(String(100), nullable=True)
    work_id = Column(String(50), nullable=True, index=True)
    category = Column(SAEnum(MagnetCategory), default=MagnetCategory.adult_eu)
    seeders = Column(Integer, default=0)
    leechers = Column(Integer, default=0)
    scraped_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
