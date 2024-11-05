from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import date, datetime
from typing import Optional
from app.user.user_model import Role, SocialProvider, Gender


class UserBase(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    profile_image: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    locale: Optional[str] = None
    age_range: Optional[str] = None
    role: Role = Role.USER


class UserCreate(UserBase):
    social_id: str
    social_provider: SocialProvider

    class Config:
        use_enum_values = True


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None


class UserInDBBase(UserBase):
    id: str
    social_id: str
    social_provider: SocialProvider
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass
