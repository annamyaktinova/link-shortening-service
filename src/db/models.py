from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from db.database import Base
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    custom_alias = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    clicks = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)