from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.user.user_model import User
from app.user.user_schema import UserCreate, UserUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def get_user_by_social_id(
    db: AsyncSession, social_id: str, provider: str
) -> Optional[User]:
    result = await db.execute(
        select(User).filter(
            User.social_id == social_id, User.social_provider == provider
        )
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(**user.dict())
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"Created new user with id: {db_user.id}")
        return db_user
    except IntegrityError:
        await db.rollback()
        logger.error(f"Failed to create user with social_id: {user.social_id}")
        raise ValueError("User with this social_id already exists")


async def update_user(
    db: AsyncSession, user_id: str, user: UserUpdate
) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if db_user:
        update_data = user.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        try:
            await db.commit()
            await db.refresh(db_user)
            logger.info(f"Updated user with id: {user_id}")
            return db_user
        except IntegrityError:
            await db.rollback()
            logger.error(f"Failed to update user with id: {user_id}")
            raise ValueError("Update failed due to integrity constraint")
    return None


async def delete_user(db: AsyncSession, user_id: str) -> Optional[User]:
    user = await get_user(db, user_id)
    if user:
        try:
            await db.delete(user)
            await db.commit()
            logger.info(f"Deleted user with id: {user_id}")
            return user
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete user with id: {user_id}. Error: {str(e)}")
            raise
    return None
