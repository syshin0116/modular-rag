from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String
import uuid


class Base(DeclarativeBase):
    __abstract__ = True
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
