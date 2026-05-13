from sqlalchemy import Column, Integer, String, Text, Enum as SAEnum, DateTime, func
from shared.database import Base
import enum

class CacheQueryType(str, enum.Enum):
    actress = "actress"
    work = "work"
    magnet = "magnet"

class SearchCache(Base):
    __tablename__ = "search_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    query_type = Column(SAEnum(CacheQueryType), nullable=False)
    result_json = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
