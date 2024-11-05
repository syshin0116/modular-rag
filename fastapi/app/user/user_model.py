from sqlalchemy import Column, String, Date, DateTime, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.model_base import Base
import enum
from uuid import uuid4


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Role(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    DEMO = "demo"


class SocialProvider(str, enum.Enum):
    GOOGLE = "google"
    KAKAO = "kakao"
    NAVER = "naver"


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    social_id = Column(String(255), unique=True, index=True, nullable=False)
    social_provider = Column(Enum(SocialProvider), nullable=False)
    email = Column(String(255), index=True)
    username = Column(String(255), index=True)
    profile_image = Column(String(255))
    birth_date = Column(Date)
    gender = Column(Enum(Gender))
    phone_number = Column(String(20))
    address = Column(String(255))
    role = Column(Enum(Role), default=Role.USER)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    full_name = Column(String(255))
    nickname = Column(String(255))
    locale = Column(String(10))
    age_range = Column(String(10))

    __table_args__ = (
        UniqueConstraint("social_provider", "social_id", name="uq_social_account"),
    )

    preference = relationship("UserPreference", back_populates="user", uselist=False)
