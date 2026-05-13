from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, func
from shared.database import Base

class BotUser(Base):
    __tablename__ = "bot_users"

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language = Column(String(10), default="zh")
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    last_active = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
